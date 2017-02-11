"""Administration configuration for the crimes app."""
from django.contrib import admin
from crimes.models import Crime

# Register your models here.


class CrimeAdmin(admin.ModelAdmin):
    """Administrator for the crime model."""

    list_display = (
        'name', 'crime_type', 'crime_class', 'sex_offense',
        'county', 'city', 'state'
    )
    empty_value_display = '---'
    list_filter = (
        'crime_type', 'crime_class', 'sex_offense',
        'county', 'city', 'state'
    )

    class Meta:
        """Declare which model we're working with."""

        model = Crime

admin.site.register(Crime, CrimeAdmin)
