"""Set of tests for the crimes app."""
from crimes.models import (
    Consequence,
    STATES,
    DURATIONS,
    CONSEQUENCE_TYPES,
    OFFENSE_CATEGORIES,
    CONSEQUENCE_CATEGORIES
)
from crimes.processing import (
    parse_offense_column,
    strip_column,
    remove_non_offenses,
    reduce_columns,
    process_spreadsheet
)
from crimes.serializers import ConsequenceSerializer

from django.test import TestCase
from factory import Factory, Sequence
from faker import Faker
import os
import pandas as pd
import random


# Create your tests here.

fake = Faker()

path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "collateral_consequence",
    "sample_data",
    "consq_NY.xls"
)
SAMPLE_DATA = pd.read_excel(path)


class ConsequenceFactory(Factory):
    """Generate new Consequence objects."""

    class Meta:
        """Set the model on the factory."""

        model = Consequence

    title = Sequence(lambda x: fake.text(255))
    citation = Sequence(lambda x: fake.text(255))
    consequence_details = Sequence(lambda x: fake.text(255))
    consequence_cat = Sequence(lambda x: random.choice(CONSEQUENCE_CATEGORIES[1:])[0])
    consequence_type = Sequence(lambda x: random.choice(CONSEQUENCE_TYPES[1:])[0])
    offense_cat = Sequence(lambda x: random.choice(OFFENSE_CATEGORIES[1:])[0])

    duration = Sequence(lambda x: random.choice(DURATIONS[1:])[0])
    duration_desc = Sequence(lambda x: fake.text(255))
    state = Sequence(lambda x: random.choice(STATES[1:])[0])


class ConsequenceTests(TestCase):
    """Tests of the Consequence model."""

    def setUp(self):
        """Create a bunch of consequence objects."""
        self.consqs = [ConsequenceFactory.create() for i in range(20)]
        for consq in self.consqs:
            consq.save()

    def test_new_consqs_have_proper_attributes(self):
        """New consequences should have a list of attributes."""
        consq = self.consqs[0]
        attrs = [
            "id", "title", "citation", "state", "consequence_cat",
            "consequence_details", "consequence_type", "duration",
            "duration_desc", "offense_cat"
        ]
        for item in attrs:
            self.assertTrue(hasattr(consq, item))

    def test_consq_str_has_right_content(self):
        """The string repr of a consequence object has proper contents."""
        consq = self.consqs[0]
        self.assertTrue(consq.title in str(consq))
        self.assertTrue(consq.state in str(consq))


class ProcessingTests(TestCase):
    """Tests of the processing pipeline."""

    sheet = SAMPLE_DATA

    def test_offense_column_str_has_removed_char(self):
        """The parse_offense_column function should remove hash symbol."""
        instr = 'Any felony;#Child Support offenses;#Other'
        self.assertFalse("#" in parse_offense_column(instr))

    def test_parsed_offense_str_is_list(self):
        """The result of the parse_offense_column function should be a list."""
        instr = 'Any felony;#Child Support offenses;#Other'
        result = parse_offense_column(instr)
        self.assertIsInstance(result, list)

    def test_offense_column_str_split_on_semicolon(self):
        """The parse_offense_column function should split on semicolons."""
        instr = 'Any felony;#Child Support offenses;#Other'
        result = parse_offense_column(instr)
        self.assertTrue(len(result) == len(instr.split(";")))
        self.assertTrue(result[1] == "Child Support offenses")

    def test_offense_column_str_input_none_returns_none_list(self):
        """The parse_offense_column function returns [None] if 'None'."""
        instr = "None"
        result = parse_offense_column(instr)
        self.assertTrue(result == [None])

    def test_strip_column_removes_leading_trailing_whitespace_in_column(self):
        """The strip_column function removes leading and trailing whitespace."""
        data = strip_column(self.sheet.fillna("None"), "Consequence Details")
        for item in data:
            self.assertFalse(item.startswith(" ") or item.endswith(" "))

    def test_strip_column_doesnt_remove_internal_whitespace(self):
        """The strip_column function should leave alone internal whitespace."""
        df = pd.DataFrame({
            "column1": ["a sentence", "another sentence"],
            "column2": [1, 2]
        })
        result = strip_column(df, "column1")
        self.assertTrue(result.column1.iloc[0] == "a sentence")

    def test_non_offenses_get_removed(self):
        """We have no need for rows that are not offenses."""
        result = remove_non_offenses(self.sheet.fillna("None"))
        for item in result["Triggering Offense Category"]:
            self.assertTrue("None" not in item)

    def test_reduce_columns_only_keeps_specified_columns(self):
        """We shouldn't have to work with every column."""
        keep_cols = ["Citation", "Title"]
        result = reduce_columns(self.sheet, keep_cols)
        self.assertTrue(len(result.columns) == 2)
        self.assertTrue("Citation" in result.columns)
        self.assertTrue("Title" in result.columns)

    def test_process_spreadsheet_creates_four_columns(self):
        """A part of the parsing is creating 4 new columns. They should exist."""
        result = process_spreadsheet(self.sheet)
        new_cols = [
            "Parsed Offense Category",
            "Parsed Additional Offenses",
            "Parsed Consequence Category",
            "Parsed Consequence Type"
        ]
        for col in new_cols:
            self.assertTrue(col in result.columns)


class SerializerTests(TestCase):
    """Tests of the Django REST serializer for the Consequence model."""

    def test_consequence_serializer_has_states(self):
        """Of its many attributes, test that the consq serializer has a state field."""
        serial = ConsequenceSerializer()
        self.assertTrue("state" in serial.data.keys())
