"""Views for the collateral_consequence app."""
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm, DataForm
from collateral_consequence.utils import (
    filter_by_offenses,
    ingest_from_remote,
    handle_uploaded_file
)
from crimes.models import Consequence, STATES, OFFENSE_CATEGORIES
from crimes.serializers import ConsequenceSerializer

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from urllib.error import HTTPError

# Create your views here.


@permission_required("crimes.add_consequence")
def add_all_states(request):
    """Retrieve and add a state's data to the database."""
    states = [
        "NY", "WA", "DC", "FED", "VA",
    ]

    for state in states:
        try:
            ingest_from_remote(state)

        except HTTPError as msg:  # pragma: no cover
            print("{} failed. Here's the message: {}".format(state, msg))

    return render(
        request,
        "main/ingest_success.html",
        {"location": state}
    )


@permission_required("crimes.add_consequence")
def add_state(request):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST" and request.POST["state"]:
        state = request.POST["state"].upper()

        try:
            ingest_from_remote(state)

            return render(
                request,
                "main/ingest_success.html",
                {"location": state, "address": scraper.make_url(state)}
            )
        except (HTTPError, KeyError):
            return render(
                request, "main/ingest_fail.html", {"location": state}
            )

    return render(
        request, "main/ingest_ready.html", {"form": StateForm()}
    )


@permission_required("crimes.add_consequence")
def add_state_from_file(request):
    """Upload and add a state's data to the database."""
    if request.POST and request.method == "POST":
        state = request.POST["state"]
        data_file = request.FILES["upload_path"]
        handle_uploaded_file(data_file, state)
        return render(
            request,
            "main/ingest_success.html",
            {"location": state, "address": "From disk"}
        )

    return render(request, "main/ingest_file.html", {
        "form": DataForm()
    })


def crime_search(request):
    """Retrieve a crime's consequences based on criteria."""
    states = [{"title": state[0], "text": state[1]} for state in STATES]
    skip_these = ["misc", "---", "felony", "misdem", "any"]
    offenses = [{"title": off[0], "text": off[1]}
                for off in OFFENSE_CATEGORIES if off[0] not in skip_these]

    return render(request, "front-end/search.html", {
        "states": states,
        "offenses": offenses
    })


@api_view(['GET'])
def consequence_pipeline(request, state=None):
    """Given a state, retrieve all consequence objects for that state."""
    state_set = [item[0] for item in STATES]
    if request.method == "GET" and state.upper() in state_set:

        consqs = Consequence.objects.filter(
            state=state.upper(),
            duration__in=["perm", "spec"]
        )

        if "offense" in request.GET:
            offenses = dict(request.GET)["offense"]
            offenses.append("Any offense")

            if "felony" in request.GET:
                offenses.append("felony")
            if "misdem" in request.GET:
                offenses.append("misdemeanor")
            consqs = filter_by_offenses(consqs, offenses)

        if "consequence_type" in request.GET:
            the_type = request.GET["consequence_type"]
            consqs = consqs.filter(consequence_type__contains=the_type)

        if "consequence_cat" in request.GET:
            the_cat = request.GET["consequence_cat"]
            consqs = consqs.filter(consequence_cat__contains=the_cat)

        consqs = consqs.exclude(consequence_type__contains="Discretion").all()
        serialized = ConsequenceSerializer(consqs, many=True)
        return Response(serialized.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)


def home_view(request):
    """View for the home route. Includes data about criminal offenses."""
    consqs = Consequence.objects
    data = {}
    for item in OFFENSE_CATEGORIES:
        if item[0] not in ["---", "misc"]:
            data.setdefault(item[0], {})
            data[item[0]]["title"] = item[1]
            data[item[0]]["count"] = consqs.filter(
                offense_cat__contains=item[1]
            ).count()

    data["any"]["count"] = consqs.filter(
        offense_cat__contains="Any offense"
    ).count()
    return render(request, "front-end/home.html", {"data": data})


def results_view(request, state=None):
    """Harvest data and get the search results."""
    context = {}
    consqs = Consequence.objects.filter(
        state=state.upper(),
        duration__in=["perm", "spec"]
    )
    url_data = dict(request.GET)
    url_data["state"] = state

    offense_list = []

    if "felony" in url_data:
        offense_list.append("felony")
        offense_list.append("Any offense")

    if "misdem" in url_data:
        offense_list.append("misdemeanor")
        offense_list.append("Any offense")

    if "offense" in url_data:
        offense_list.append("Any offense")
        for offense in url_data["offense"]:
            try:
                offense_list.append(dict(OFFENSE_CATEGORIES)[offense])
            except KeyError:
                pass

    # TODO: post message if not a us citizen
    # -- something about asking about potential immigration consequences

    # TODO: filter down if receiving government benefits
    # -- if user isn't on government benefits, hide consequence category

    # TODO: filter down if living in government housing
    # -- if user isn't living in government housing, hide consequence category

    consqs = filter_by_offenses(consqs, offense_list)
    result = consqs.exclude(consequence_type__contains="Discretion")
    context["count"] = result.count()
    context["query_params"] = url_data
    return render(request, "front-end/results.html", context)
