"""Views for the collateral_consequence app."""
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm
from crimes.models import Consequence, STATES, OFFENSE_CATEGORIES
from crimes.processing import process_spreadsheet
from crimes.serializers import ConsequenceSerializer

from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.db.transaction import TransactionManagementError
from django.db.utils import DataError
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
            ingest_rows(state)

        except HTTPError as msg:
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
            ingest_rows(state)

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
    return render(request, "", {})


def crime_search(request):
    """Retrieve a crime's consequences based on criteria."""
    states = [{"title": state[0], "text": state[1]} for state in STATES]
    skip_these = ["misc", "---", "felony", "misdem", "any"]
    offs = [{"title": off[0], "text": off[1]}
            for off in OFFENSE_CATEGORIES if off[0] not in skip_these]

    return render(request, "front-end/search.html", {
        "states": states,
        "offenses": offs
    })


@api_view(['GET'])
def consequence_pipeline(request, state=None):
    """Given a state, retrieve all consequence objects for that state."""
    state_set = [item[0] for item in STATES]
    state = state.upper()
    if request.method == "GET" and state in state_set:

        consqs = Consequence.objects.filter(
            state=state,
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


def filter_by_offenses(query_manager, offenses):
    """Filter consequences down by offense(s)."""
    complex_query = Q(offense_cat__contains=offenses[0])
    if len(offenses) > 1:
        for offense in offenses[1:]:
            complex_query |= Q(offense_cat__contains=offense)

    return query_manager.filter(complex_query)


def ingest_rows(state):
    """Given a dataframe, input new data into the database."""
    if not Consequence.objects.filter(state=state).count():
        data = scraper.get_data(scraper.make_url(state))
        processed_data = process_spreadsheet(data)
        duration_dict = {
            'Specific Term': "spec",
            'N/A (background check, general relief)': "bkg",
            'Conditional': "cond",
            'Permanent/Unspecified': "perm",
            'None': 'none'
        }

        all_offenses = []
        all_consequence_cats = []
        all_consequence_types = []
        for idx in range(len(processed_data)):
            citation = processed_data.iloc[idx]

            cols = [
                "Parsed Offense Category",
                "Parsed Consequence Category",
                "Parsed Consequence Type"
            ]
            offenses = [item.replace(",", "") for item in citation[cols[0]]]
            categories = [item.replace(",", "") for item in citation[cols[1]]]
            con_types = [item.replace(",", "") for item in citation[cols[2]]]

            all_offenses.extend(offenses)
            all_consequence_cats.extend(categories)
            all_consequence_types.extend(con_types)

            new_consq = Consequence(
                title=citation.Title,
                citation=citation.Citation,
                state=state,
                consequence_details=citation["Consequence Details"],
                duration=duration_dict[citation["Duration Category"]],
                duration_desc=citation["Duration Description"],
                offense_cat=offenses,
                consequence_cat=categories,
                consequence_type=con_types
            )
            try:
                new_consq.save()
            except (DataError, TransactionManagementError):  # pragma: no cover
                print("Broke at: ", citation.Title)
                print(
                    "Consequence details: ",
                    len(citation["Consequence Details"])
                )
                print("Duration: ", len(citation["Duration Category"]))
                print(
                    "Duration Description: ",
                    len(citation["Duration Description"])
                )
                print("Offense list: ", len(offenses))
                print("Consequence categories list: ", len(categories))
                print(
                    "Consequence type list: {}\n\n".format(len(con_types))
                )
                pass


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

    data["any"]["count"] = consqs.filter(offense_cat__contains="Any offense").count()
    return render(request, "front-end/home.html", {"data": data})


def results_view(request, state=None):
    """Harvest data and get the search results."""
    context = {}
    consqs = Consequence.objects.filter(
        state=state,
        duration__in=["perm", "spec"]
    )
    url_data = dict(request.GET)
    url_data["state"] = state
    offense_list = ["Any offense"]

    if "felony" in url_data:
        offense_list.append("felony")

    if "misdem" in url_data:
        offense_list.append("misdemeanor")

    if "offense" in url_data:
        for offense in url_data["offense"]:
            try:
                offense_list.append(dict(OFFENSE_CATEGORIES)[offense])
            except KeyError:
                pass

    result = filter_by_offenses(consqs, offense_list).exclude(consequence_type__contains="Discretion")
    # context["mandatory"] = result.filter(
    #     consequence_type__contains="Mandatory"
    # ).all()
    # context["possible"] = result.filter(
    #     consequence_type__contains="Background"
    # ).all()  # don't forget to exclude discretionary and discretionary (waiver)
    context["count"] = result.count()
    context["query_params"] = url_data
    return render(request, "front-end/results.html", context)
