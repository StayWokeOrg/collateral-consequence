"""Serializer for the Consequence model."""
from rest_framework import serializers
from crimes.models import Consequence


class ConsequenceSerializer(serializers.ModelSerializer):
    """Serializer for the Consequence model."""

    class Meta:
        """Model definition and field selection."""

        model = Consequence
        fields = (
            "id", "title", "citation", "state", "consequence_cat",
            "consequence_details", "consequence_type", "duration",
            "duration_desc", "offense_cat"
        )
