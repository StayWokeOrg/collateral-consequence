"""Set of tests for the collateral consequence application."""
from django.test import TestCase, Client, RequestFactory
from collateral_consequence.views import add_state


class IngestionTests(TestCase):
    """Test ingestion pipeline."""

    def setUp(self):
        """Set up for the ingestion tests."""
        self.request_builder = RequestFactory()
        self.client = Client()

    def test_add_state_get_is_200(self):
        """."""
        req = self.request_builder.get("/foo")
        response = add_state(req, abbr="WAT")
        self.assertTrue(response.status_code == 200)

    def test_add_state_post_bad_abbr_fails(self):
        """."""
        req = self.request_builder.post("/foo")
        response = add_state(req, abbr="WAT")
        self.assertTrue("unable" in str(response.content))

    def test_add_state_post_good_abbr_succeeds(self):
        """."""
        req = self.request_builder.post("/foo")
        response = add_state(req, abbr="NY")
        self.assertTrue("success" in str(response.content))
