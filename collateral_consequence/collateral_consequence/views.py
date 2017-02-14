"""Views for the collateral_consequence app."""
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm
from crimes.models import Crime, STATES
from crimes.processing import process_spreadsheet
from crimes.serializers import CrimeSerializer

from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from urllib.error import HTTPError

# Create your views here.


@permission_required("crimes.add_crime")
def add_state(request):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST" and request.POST["state"]:
        state = request.POST["state"]

        try:
            if not Crime.objects.filter(state=state).count():
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
    return render(request, "", {})


@api_view(['GET'])
def crimes_by_state(request, state=None):
    """Given a state, retrieve all crime objects for that state."""
    if request.method == "GET" and state in STATES:
        crimes = Crime.objects.filter(state=state).all()
        serialized = CrimeSerializer(crimes, many=True)
        return Response(serialized.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def offense_types_by_state(request, state=None):
#     """Given a state, retrieve narrowed offense types."""
#     if request.method == 'GET':
#         crimes = Crime.objects.filter(state=state).all()
#     return render(request, "", {})


def citations_by_state(request):
    """Given a state, retrieve all the citations for that state."""
    return render(request, "", {})


def crime_titles_by_state(request):
    """Given a state, retrieve all the crime titles for that state."""
    return render(request, "", {})


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
        new_crime = Crime(
            title=citation.Title,
            citation=citation.Citation,
            state=state,
            consequence_details=citation["Consequence Details"],
            duration=duration_dict[citation["Duration Category"]],
            duration_desc=citation["Duration Description"],
            offense_cat=citation["Parsed Offense Category"],
            consequence_cat=citation["Parsed Consequence Category"],
            consequence_type=citation["Parsed Consequence Type"]
        )
        new_crime.save()
