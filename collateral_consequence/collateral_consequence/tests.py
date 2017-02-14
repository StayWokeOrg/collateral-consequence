"""Set of tests for the collateral consequence application."""
from collateral_consequence.views import add_state
from crimes.models import Consequence, STATES

from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse_lazy

from bs4 import BeautifulSoup as Soup
import mock
import os
import pandas as pd


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
        self.user = User(username="admin")
        self.user.set_password = "potatoes"
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

    def test_add_state_get_is_200(self):
        """."""
        req = self.request_builder.get("/foo")
        req.user = self.user
        response = add_state(req)
        self.assertTrue(response.status_code == 200)

    def test_add_state_post_bad_abbr_fails(self):
        """."""
        req = self.request_builder.post("/foo", {"state": "WAT"})
        req.user = self.user
        response = add_state(req)
        self.assertTrue("unable" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_post_good_abbr_succeeds(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.user
        response = add_state(req)
        self.assertTrue("success" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_post_good_abbr_has_url(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.user
        response = add_state(req)
        self.assertTrue("https://niccc" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_twice_doesnt_duplicate(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.user
        add_state(req)
        count1 = Consequence.objects.filter(state='NY').count()
        add_state(req)
        count2 = Consequence.objects.filter(state='NY').count()
        self.assertEqual(count1, count2)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_route_get_is_200(self, get_data):
        """."""
        response = self.client.get(reverse_lazy("add_state"))
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_route_get_has_select_list(self, get_data):
        """."""
        response = self.client.get(reverse_lazy("add_state"))
        html = Soup(response.content, "html5lib")
        self.assertEqual(len(html.find_all("option")), len(STATES) - 1)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_route_post_bad_state_is_fail(self, get_data):
        """."""
        response = self.client.post(reverse_lazy("add_state"), {
            "state": "WAT"
        })
        self.assertTemplateUsed(response, "main/ingest_fail.html")

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=SAMPLE_DATA
    )
    def test_add_state_route_post_bad_state_is_success(self, get_data):
        """."""
        response = self.client.post(reverse_lazy("add_state"), {
            "state": "NY"
        })
        self.assertTemplateUsed(response, "main/ingest_success.html")
