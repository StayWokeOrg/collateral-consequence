"""Views for the collateral_consequence app."""
from django.shortcuts import render
from crimes.models import Crime
from .scraper import make_url, STATES

# Create your views here.


def add_state(request, abbr=None):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST":
        if abbr.upper() not in STATES:
            # state abbr is bad
            return render(
                request,
                "main/ingest_fail.html",
                {"location": abbr}
            )
        else:
            # state abbr is good
            return render(
                request,
                "main/ingest_success.html",
                {"location": abbr}
            )
    else:
        return render(
            request,
            "main/ingest_ready.html",
            {}
        )
