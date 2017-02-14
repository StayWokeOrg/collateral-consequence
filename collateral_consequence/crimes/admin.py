"""Administration configuration for the crimes app."""
from django.contrib import admin
from crimes.models import Crime

# Register your models here.


class CrimeAdmin(admin.ModelAdmin):
    """Administrator for the crime model."""

    list_display = (
        'title', 'citation', 'duration', 'state'
    )
    empty_value_display = '---'
    list_filter = (
        'duration', 'state', 'consequence_type', 'consequence_cat'
    )

    class Meta:
        """Declare which model we're working with."""

        model = Crime

admin.site.register(Crime, CrimeAdmin)
