"""Forms for Collateral Consequence."""
from django import forms
from .scraper import STATES


states_reversed = []
for key, val in STATES.items():
    states_reversed.append((key.lower(), key))


class StateForm(forms.Form):
    """Form for choosing a state to upload."""

    state = forms.ChoiceField(choices=states_reversed)
