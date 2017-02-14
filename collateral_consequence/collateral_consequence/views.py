"""Views for the collateral_consequence app."""
from django.shortcuts import render
from crimes.models import Crime
from crimes.processing import process_spreadsheet
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm
from urllib.error import HTTPError

# Create your views here.


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
