"""Serializer for the Crime model."""
from rest_framework import serializers
from crimes.models import Crime


class CrimeSerializer(serializers.ModelSerializer):
    """Serializer for the Crime model."""

    class Meta:
        """Model definition and field selection."""

        model = Crime
        fields = (
            "id", "title", "citation", "state", "consequence_category",
            "consequence_details", "consequence_type", "duration",
            'any_felony', 'any_misdemeanor', 'any_offense',
            'child_support', 'citation', 'controlled_substances', 'corruption',
            'election_related', 'fraud', 'moral_turpitude', 'motor_vehicle',
            'recreational_license', 'sex_offense', 'violence', 'weapons'
        )
