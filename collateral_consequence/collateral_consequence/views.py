"""Views for the collateral_consequence app."""
from django.shortcuts import render
from crimes.models import Crime
from collateral_consequence import scraper
from collateral_consequence.forms import StateForm
from urllib.error import HTTPError

# Create your views here.


def add_state(request):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST" and request.POST["state"]:
        state = request.POST["state"]

        try:

            data = scraper.get_data(scraper.make_url(state))
            # process data
            return render(
                request,
                "main/ingest_success.html",
                {
                    "location": state,
                    "address": scraper.make_url(state)
                }
            )
        except (HTTPError, KeyError):
            return render(
                request,
                "main/ingest_fail.html",
                {"location": state}
            )

    return render(
        request,
        "main/ingest_ready.html",
        {"form": StateForm()}
    )
