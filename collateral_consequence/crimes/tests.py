"""Set of tests for the crimes app."""
from crimes.models import Crime, STATES, DURATIONS
from django.test import TestCase
from factory import Factory, Sequence
from faker import Faker
import os
import pandas as pd
import random

# Create your tests here.

fake = Faker()


class CrimeFactory(Factory):
    """Generate new Crime objects."""

    class Meta:
        """Set the model on the factory."""

        model = Crime

    title = Sequence(lambda x: fake.text(255))
    citation = Sequence(lambda x: fake.text(255))
    consequence_category = Sequence(lambda x: fake.text(255))
    consequence_details = Sequence(lambda x: fake.text(255))
    consequence_type = Sequence(lambda x: fake.text(255))

    duration = Sequence(lambda x: random.choice(DURATIONS[1:])[0])
    state = Sequence(lambda x: random.choice(STATES[1:])[0])


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
            "title", "citation", "state", "consequence_category",
            "consequence_details", "consequence_type", "duration"
        ]
        for item in attrs:
            self.assertTrue(hasattr(crime, item))

    def test_crime_str_has_right_content(self):
        """The string representation of a crime object has proper contents."""
        crime = self.crimes[0]
        self.assertTrue(crime.title in str(crime))
        self.assertTrue(crime.state in str(crime))


class ProcessingTests(TestCase):
    """Tests of the processing pipeline."""

    sheets_dir = '/Users/Nick/Documents/staywoke/collateral-consequence/dev_tools/scraped_files'
    sheet = pd.read_excel(os.path.join(sheets_dir, "consq_MI.xls"))

    def test_offense_column_str_has_removed_char(self):
        """The parse_offense_column function should remove hash symbol."""
        from crimes.processing import parse_offense_column
        instr = 'Any felony;#Child Support offenses;#Other'
        self.assertFalse("#" in parse_offense_column(instr))

    def test_offense_column_str_split_on_semicolon(self):
        """The parse_offense_column function should split on semicolons."""
        from crimes.processing import parse_offense_column
        instr = 'Any felony;#Child Support offenses;#Other'
        result = parse_offense_column(instr)
        self.assertTrue(len(result) == len(instr.split(";")))
        self.assertTrue(result[1] == "Child Support offenses")

    def test_offense_column_str_input_none_returns_none_list(self):
        """The parse_offense_column function returns [None] if 'None'."""
        from crimes.processing import parse_offense_column
        instr = "None"
        result = parse_offense_column(instr)
        self.assertTrue(result == [None])

    def test_strip_column_removes_leading_trailing_whitespace_in_column(self):
        """The strip_column function removes leading and trailing whitespace."""
        from crimes.processing import strip_column
        series = strip_column(self.sheet.fillna("None"), "Consequence Details")
        for item in series:
            self.assertFalse(item.startswith(" ") or item.endswith(" "))
