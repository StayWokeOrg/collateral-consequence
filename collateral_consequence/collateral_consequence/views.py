"""Views for the collateral_consequence app."""
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm
from crimes.models import Consequence, STATES, OFFENSE_CATEGORIES
from crimes.processing import process_spreadsheet
from crimes.serializers import ConsequenceSerializer

from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from urllib.error import HTTPError

# Create your views here.


@permission_required("crimes.add_consequence")
def add_state(request):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST" and request.POST["state"]:
        state = request.POST["state"].upper()

        try:
            if not Consequence.objects.filter(state=state).count():
                data = scraper.get_data(scraper.make_url(state))
                ingest_rows(data, state)

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


def crime_search(request):
    """Retrieve a crime's consequences based on criteria."""
    states = []
    offenses = []
    for state in STATES:
        states.append({
            "title": state[0],
            "text": state[1],
        })

    skip_these = ["misc", "---", "felony", "misdem", "any"]
    for offense in OFFENSE_CATEGORIES:
        if offense[0] not in skip_these:
            offenses.append({
                "title": offense[0],
                "text": offense[1]
            })
    return render(request, "front-end/search.html", {
        "states": states,
        "offenses": offenses
    })


@api_view(['GET'])
def consequences_by_state(request, state=None):
    """Given a state, retrieve all consequence objects for that state."""
    state_set = [item[0] for item in STATES]
    if request.method == "GET" and state.upper() in state_set:

        consqs = Consequence.objects.filter(state=state)
        if "offense" in request.GET:
            offense = request.GET["offense"]
            consqs = consqs.filter(offense_cat__contains=offense)

        if "consequence_type" in request.GET:
            the_type = request.GET["consequence_type"]
            consqs = consqs.filter(consequence_type__contains=the_type)

        if "consequence_cat" in request.GET:
            the_cat = request.GET["consequence_cat"]
            consqs = consqs.filter(consequence_cat__contains=the_cat)

        consqs = consqs.all()
        serialized = ConsequenceSerializer(consqs, many=True)
        return Response(serialized.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)


def ingest_rows(data, state):
    """Given a dataframe, input new data into the database."""
    processed_data = process_spreadsheet(data)
    duration_dict = {
        'Specific Term': "spec",
        'N/A (background check, general relief)': "bkg",
        'Conditional': "cond",
        'Permanent/Unspecified': "perm",
        'None': 'none'
    }
    for idx in range(len(processed_data)):
        citation = processed_data.iloc[idx]
        offenses = [item.replace(",", "") for item in citation["Parsed Offense Category"]]
        categories = [item.replace(",", "") for item in citation["Parsed Consequence Category"]]
        con_types = [item.replace(",", "") for item in citation["Parsed Consequence Type"]]

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
        new_consq.save()


def home_view(request):
    """View for the home route. Includes data about criminal offenses."""
    consqs = Consequence.objects
    data = {}
    for item in OFFENSE_CATEGORIES:
        if item[0] not in ["---", "misc"]:
            data.setdefault(item[0], {})
            data[item[0]]["title"] = item[1]
            data[item[0]]["count"] = consqs.filter(offense_cat__contains=item[1]).count()
    return render(request, "front-end/home.html", {"data": data})


def results_view(request):
    """Harvest data and get the search results."""
    return render(request, "", {})
