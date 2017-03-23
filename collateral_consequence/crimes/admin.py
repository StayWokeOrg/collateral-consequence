"""Administration configuration for the crimes app."""
from django.contrib import admin
from crimes.models import Consequence

# Register your models here.


class ConsequenceAdmin(admin.ModelAdmin):
    """Administrator for the consequence model."""

    list_display = (
        'title', 'citation', 'duration', 'state'
    )
    empty_value_display = '---'
    list_filter = (
        'duration', 'state', 'consequence_type', 'consequence_cat'
    )

    class Meta:
        """Declare which model we're working with."""

        model = Consequence

admin.site.register(Consequence, ConsequenceAdmin)
