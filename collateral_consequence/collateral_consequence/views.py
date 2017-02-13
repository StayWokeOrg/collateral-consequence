"""Views for the collateral_consequence app."""
from django.shortcuts import render
from crimes.models import Crime
from collateral_consequence.scraper import make_url, STATES
from collateral_consequence.forms import StateForm

# Create your views here.


def add_state(request):
    """Retrieve and add a state's data to the database."""
    if request.method == "POST":
        state = request.POST["state"]
        if state not in STATES:
            # provided state is bad
            return render(
                request,
                "main/ingest_fail.html",
                {"location": state}
            )
        else:
            # provided  state is good
            return render(
                request,
                "main/ingest_success.html",
                {
                    "location": state,
                    "address": make_url(state)
                }
            )
    return render(
        request,
        "main/ingest_ready.html",
        {"form": StateForm()}
    )
