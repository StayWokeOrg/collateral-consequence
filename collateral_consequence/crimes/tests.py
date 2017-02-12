"""Set of tests for the crimes app."""
from django.test import TestCase
from crimes.models import Crime, CRIME_TYPES, CRIME_CLASSES, STATES
import random
import factory
from faker import Faker

# Create your tests here.

fake = Faker()


class CrimeFactory(factory.Factory):
    """Generate new Crime objects."""

    class Meta:
        """Set the model on the factory."""

        model = Crime

    name = factory.Sequence(lambda x: fake.text(30))
    crime_type = factory.Sequence(lambda x: random.choice(CRIME_TYPES[1:])[0])
    crime_class = factory.Sequence(lambda x: random.choice(CRIME_CLASSES[1:])[0])
    sex_offense = factory.Sequence(lambda x: fake.boolean())
    state = factory.Sequence(lambda x: random.choice(STATES[1:])[0])


class CrimeTests(TestCase):
    """Tests of the Crime model."""

    def setUp(self):
        """Create a bunch of crime objects."""
        self.crimes = [CrimeFactory.create() for i in range(20)]
        for crime in self.crimes:
            crime.save()

    def test_new_crimes_have_proper_attributes(self):
        """New crimes should have a list of attributes."""
        crime = self.crimes[0]
        attrs = [
            "name", "crime_type", "crime_class", "sex_offense",
            "county", "city", "state"
        ]
        for item in attrs:
            self.assertTrue(hasattr(crime, item))

    def test_crime_str_has_right_content(self):
        """The string representation of a crime object has proper contents."""
        crime = self.crimes[0]
        self.assertTrue(crime.name in str(crime))
        self.assertTrue(crime.crime_type in str(crime))
        self.assertTrue(crime.crime_class in str(crime))
        self.assertTrue(crime.state in str(crime))
