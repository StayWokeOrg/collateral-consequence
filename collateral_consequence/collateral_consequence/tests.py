"""Set of tests for the collateral consequence application."""
from django.test import TestCase, Client, RequestFactory
from collateral_consequence.views import add_state
import mock
import pandas as pd
import os


path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sample_data",
    "consq_NY.xls"
)
SAMPLE_DATA = pd.read_excel(path)


class IngestionTests(TestCase):
    """Test ingestion pipeline."""

    def setUp(self):
        """Set up for the ingestion tests."""
        self.request_builder = RequestFactory()
        self.client = Client()

    def test_add_state_get_is_200(self):
        """."""
        req = self.request_builder.get("/foo")
        response = add_state(req)
        self.assertTrue(response.status_code == 200)

    def test_add_state_post_bad_abbr_fails(self):
        """."""
        req = self.request_builder.post("/foo", {"state": "WAT"})
        response = add_state(req)
        self.assertTrue("unable" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_post_good_abbr_succeeds(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        response = add_state(req)
        self.assertTrue("success" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_post_good_abbr_has_url(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        response = add_state(req)
        self.assertTrue("https://niccc" in str(response.content))

