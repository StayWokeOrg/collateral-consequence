"""Administration configuration for the crimes app."""
from django.contrib import admin
from crimes.models import Crime

# Register your models here.


class CrimeAdmin(admin.ModelAdmin):
    """Administrator for the crime model."""

    list_display = ('name')

    class Meta:
        """Declare which model we're working with."""

        model = Crime

admin.site.register(Crime, CrimeAdmin)
