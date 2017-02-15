"""Set of tests for the collateral consequence application."""
from collateral_consequence.views import (
    add_state,
    add_all_states
)
from collateral_consequence.scraper import get_data
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
    "sample_data"
)
NY_DATA = pd.read_excel(os.path.join(path, "consq_NY.xls"))
WA_DATA = pd.read_excel(os.path.join(path, "consq_WA.xls"))
DC_DATA = pd.read_excel(os.path.join(path, "consq_DC.xls"))
VA_DATA = pd.read_excel(os.path.join(path, "consq_VA.xls"))
FED_DATA = pd.read_excel(os.path.join(path, "consq_FED.xls"))


class IngestionTests(TestCase):
    """Test ingestion pipeline."""

    def setUp(self):
        """Set up for the ingestion tests."""
        self.request_builder = RequestFactory()
        self.client = Client()
        self.auth_user = self.create_user("admin", True)
        self.unauth_user = self.create_user("tugboat", False)
        self.client.force_login(self.auth_user)

    def create_user(self, username=None, superuser=False):
        """Create a user fixture."""
        user = User(username=username)
        user.is_superuser = superuser
        user.set_password = "potatoes"
        user.save()
        return user

    def test_add_state_get_is_200(self):
        """."""
        req = self.request_builder.get("/foo")
        req.user = self.auth_user
        response = add_state(req)
        self.assertTrue(response.status_code == 200)

    def test_add_state_post_bad_abbr_fails(self):
        """."""
        req = self.request_builder.post("/foo", {"state": "WAT"})
        req.user = self.auth_user
        response = add_state(req)
        self.assertTrue("unable" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_post_good_abbr_succeeds(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.auth_user
        response = add_state(req)
        self.assertTrue("success" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_post_good_abbr_has_url(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.auth_user
        response = add_state(req)
        self.assertTrue("https://niccc" in str(response.content))

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_twice_doesnt_duplicate(self, get_data):
        """."""
        req = self.request_builder.post("/foo", {"state": "NY"})
        req.user = self.auth_user
        add_state(req)
        count1 = Consequence.objects.filter(state='NY').count()
        add_state(req)
        count2 = Consequence.objects.filter(state='NY').count()
        self.assertEqual(count1, count2)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_route_get_is_200(self, get_data):
        """."""
        response = self.client.get(reverse_lazy("add_state"))
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_route_get_has_select_list(self, get_data):
        """."""
        response = self.client.get(reverse_lazy("add_state"))
        html = Soup(response.content, "html5lib")
        self.assertEqual(len(html.find_all("option")), len(STATES) - 1)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_route_post_bad_state_is_fail(self, get_data):
        """."""
        response = self.client.post(reverse_lazy("add_state"), {
            "state": "WAT"
        })
        self.assertTemplateUsed(response, "main/ingest_fail.html")

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def test_add_state_route_post_bad_state_is_success(self, get_data):
        """."""
        response = self.client.post(reverse_lazy("add_state"), {
            "state": "NY"
        })
        self.assertTemplateUsed(response, "main/ingest_success.html")

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        side_effect=[NY_DATA, WA_DATA, DC_DATA, FED_DATA, VA_DATA]
    )
    def test_add_all_states_is_status_200_auth_user(self, get_data):
        """."""
        req = self.request_builder.get("/foo-bar")
        req.user = self.auth_user
        response = add_all_states(req)
        self.assertTrue(response.status_code == 200)

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        side_effect=[NY_DATA, WA_DATA, DC_DATA, FED_DATA, VA_DATA]
    )
    def test_add_all_states_is_status_302_not_auth_user(self, get_data):
        """."""
        req = self.request_builder.get("/foo-bar")
        req.user = self.unauth_user
        response = add_all_states(req)
        self.assertTrue(response.status_code == 302)


class ScraperTests(TestCase):
    """Tests for scraper.py."""

    def test_get_data_returns_dataframe(self):
        """The get_data function is only supposed to return a data frame."""
        result = get_data(os.path.join(path, "consq_NY.xls"))
        self.assertIsInstance(result, pd.core.frame.DataFrame)
