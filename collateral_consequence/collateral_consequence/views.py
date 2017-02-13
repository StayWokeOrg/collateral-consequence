"""Views for the collateral_consequence app."""
from django.shortcuts import render
from crime.models import Crime

# Create your views here.


def add_state(request, abbr=None):
    """Retrieve and add a state's data to the database."""
    return render(request, "", {})
