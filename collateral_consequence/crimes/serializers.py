"""Serializer for the Crime model."""
from rest_framework import serializers
from crimes.models import Crime


class CrimeSerializer(serializers.ModelSerializer):
    """Serializer for the Crime model."""

    class Meta:
        """Model definition and field selection."""

        model = Crime
        fields = (
            'name', 'crime_type', 'crime_class', 'sex_offense',
            'county', 'city', 'state'
        )
