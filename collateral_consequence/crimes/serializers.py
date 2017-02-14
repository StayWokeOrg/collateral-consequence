"""Serializer for the Crime model."""
from rest_framework import serializers
from crimes.models import Crime


class CrimeSerializer(serializers.ModelSerializer):
    """Serializer for the Crime model."""

    class Meta:
        """Model definition and field selection."""

        model = Crime
        fields = (
            "id", "title", "citation", "state", "consequence_cat",
            "consequence_details", "consequence_type", "duration",
            "duration_desc", "offense_cat"
        )
