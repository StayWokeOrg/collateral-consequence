"""Set of tests for the collateral consequence application."""
from collateral_consequence.views import (
    add_state,
    add_all_states,
    consequence_pipeline,
    crime_search,
    home_view,
    ingest_rows
)
from collateral_consequence.scraper import get_data
from crimes.models import Consequence, STATES, OFFENSE_CATEGORIES

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TransactionTestCase, TestCase, Client, RequestFactory
from django.urls import reverse_lazy

from bs4 import BeautifulSoup as Soup
import json
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


class IngestionTests(TransactionTestCase): # <-- use for Travis only
# class IngestionTests(TestCase):
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

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def fill_db(self, get_data):
        """Fill the database with consequences."""
        ingest_rows("NY")

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


class SearchTests(TestCase):
    """Test search pipeline."""

    def setUp(self):
        """Set up for the search tests."""
        self.request_builder = RequestFactory()
        self.client = Client()

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def fill_db(self, get_data):
        """Fill the database with consequences."""
        ingest_rows("NY")

    def parsed_json_response(self, request):
        """."""
        response = consequence_pipeline(request, state="ny")
        parsed_content = json.loads(response.rendered_content.decode('utf8'))
        return parsed_content

    def test_crime_search_is_status_200(self):
        """."""
        req = self.request_builder.get("/foo-bar")
        response = crime_search(req)
        self.assertTrue(response.status_code == 200)

    def test_crime_search_has_states(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        self.assertTrue("states" in str(response.context))

    def test_crime_search_has_lists_of_dicts_of_states(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        states = response.context["states"]
        self.assertIsInstance(states, list)
        for state in states:
            self.assertIsInstance(state, dict)

    def test_crime_search_has_abbrev_long_name_pairs_of_states(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        states = response.context["states"]
        for state in states:
            self.assertTrue(len(state["title"]) <= 3)
            self.assertTrue(len(state["text"]) >= 4)

    def test_crime_search_has_offenses(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        self.assertTrue("offenses" in str(response.context))

    def test_crime_search_has_lists_of_dicts_of_offenses(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        offenses = response.context["offenses"]
        self.assertIsInstance(offenses, list)
        for offense in offenses:
            self.assertIsInstance(offense, dict)

    def test_crime_search_has_abbrev_long_name_pairs_of_offenses(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        offenses = response.context["offenses"]
        for offense in offenses:
            self.assertFalse(' ' in offense["title"])
            self.assertTrue(len(offense["text"]) >= 5)

    def test_crime_search_uses_search_template(self):
        """."""
        response = self.client.get(reverse_lazy('crime_search'))
        self.assertTemplateUsed(response, "front-end/search.html")

    def test_get_consequence_pipeline_is_200(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo")
        response = consequence_pipeline(req, state="NY")
        self.assertTrue(response.status_code == 200)

    def test_get_consequences_by_lower_state_is_200(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo")
        response = consequence_pipeline(req, state="ny")
        self.assertTrue(response.status_code == 200)

    def test_get_consequences_returns_json(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo")
        response = consequence_pipeline(req, state="ny")
        self.assertTrue(response.accepted_media_type == "application/json")

    def test_get_consequences_returns_right_num_consequences(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo")
        parsed_content = self.parsed_json_response(req)
        self.assertTrue(len(parsed_content) == Consequence.objects.count())

    def test_get_consequences_consequence_has_all_fields(self):
        """."""
        self.fill_db()
        fields = (
            "id", "title", "citation", "state", "consequence_cat",
            "consequence_details", "consequence_type", "duration",
            "duration_desc", "offense_cat"
        )
        req = self.request_builder.get("/foo")
        parsed_content = self.parsed_json_response(req)
        for field in fields:
            self.assertTrue(field in parsed_content[0])

    def test_post_consequences_is_bad_request(self):
        """."""
        req = self.request_builder.post("/foo")
        response = consequence_pipeline(req, state="ny")
        self.assertTrue(response.status_code == 405)

    def test_get_consequences_bad_state_is_bad_request(self):
        """."""
        req = self.request_builder.get("/foo")
        response = consequence_pipeline(req, state="china")
        self.assertTrue(response.status_code == 400)

    def test_get_consequences_with_offense_shows_only_that_offense(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": "felony"
        })
        parsed_content = self.parsed_json_response(req)
        felony_consequences = Consequence.objects.filter(
            offense_cat__contains="felony"
        ).count()
        self.assertTrue(len(parsed_content) == felony_consequences)

    def test_get_consequences_with_bad_offense_returns_none(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": "pickles"
        })
        parsed_content = self.parsed_json_response(req)
        self.assertTrue(len(parsed_content) == 0)

    def test_get_consequences_with_multiple_offenses_returns_all_of_both(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": ["vehicle", "weapons"]
        })
        parsed_content = self.parsed_json_response(req)
        consqs1 = Q(offense_cat__contains="vehicle")
        consqs2 = Q(offense_cat__contains="weapons")
        complex_query = consqs1 | consqs2
        result_count = Consequence.objects.filter(
            complex_query, state="NY"
        ).count()
        self.assertTrue(len(parsed_content) == result_count)

    def test_get_mandatory_consequences_returns_right_count_consequences(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "consequence_type": "auto"
        })
        parsed_content = self.parsed_json_response(req)
        mandatories = Consequence.objects.filter(
            consequence_type__contains="auto"
        ).count()
        self.assertTrue(len(parsed_content) == mandatories)

    def test_get_bad_consequence_type_returns_none(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "consequence_type": "magic"
        })
        parsed_content = self.parsed_json_response(req)
        self.assertTrue(len(parsed_content) == 0)

    def test_get_consequence_type_and_offense_returns_proper_count(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": "weapons",
            "consequence_type": "auto"
        })
        parsed_content = self.parsed_json_response(req)
        consqs_ct = Consequence.objects.filter(
            state="NY",
            offense_cat__contains="weapons",
            consequence_type__contains="auto"
        ).count()
        self.assertTrue(len(parsed_content) == consqs_ct)

    def test_get_consequence_type_and_many_offenses_returns_proper_count(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": ["weapons", "vehicle"],
            "consequence_type": "auto"
        })
        parsed_content = self.parsed_json_response(req)
        consqs1 = Q(offense_cat__contains="vehicle")
        consqs2 = Q(offense_cat__contains="weapons")
        complex_query = consqs1 | consqs2
        consqs_ct = Consequence.objects.filter(
            complex_query,
            state="NY",
            consequence_type__contains="auto"
        ).count()
        self.assertTrue(len(parsed_content) == consqs_ct)

    def test_bad_consequence_type_and_many_offenses_returns_none(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": ["weapons", "vehicle"],
            "consequence_type": "boogy"
        })
        parsed_content = self.parsed_json_response(req)
        self.assertTrue(len(parsed_content) == 0)

    def test_get_consequence_type_one_bad_offense_returns_proper_count(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "offense": ["weapons", "fluffiness"],
            "consequence_type": "auto"
        })
        parsed_content = self.parsed_json_response(req)
        consqs_ct = Consequence.objects.filter(
            offense_cat__contains="weapons",
            state="NY",
            consequence_type__contains="auto"
        ).count()
        self.assertTrue(len(parsed_content) == consqs_ct)

    def test_get_education_consequences_returns_proper_count(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "consequence_cat": "education"
        })
        parsed_content = self.parsed_json_response(req)
        consqs_ct = Consequence.objects.filter(
            state="NY", consequence_cat__contains="education"
        ).count()
        self.assertTrue(len(parsed_content) == consqs_ct)

    def test_bad_consequence_cat_returns_none(self):
        """."""
        self.fill_db()
        req = self.request_builder.get("/foo", {
            "consequence_cat": "candy"
        })
        parsed_content = self.parsed_json_response(req)
        self.assertTrue(len(parsed_content) == 0)


class ScraperTests(TestCase):
    """Tests for scraper.py."""

    def test_get_data_returns_dataframe(self):
        """The get_data function is only supposed to return a data frame."""
        result = get_data(os.path.join(path, "consq_NY.xls"))
        self.assertIsInstance(result, pd.core.frame.DataFrame)


class HomeViewTests(TestCase):
    """Tests for the home view."""

    def setUp(self):
        """Set up for the home view tests."""
        self.request_builder = RequestFactory()
        self.client = Client()

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def fill_db(self, get_data):
        """Fill the database with consequences."""
        ingest_rows("NY")

    def test_home_view_returns_200(self):
        """."""
        req = self.request_builder.get("/foo")
        response = home_view(req)
        self.assertTrue(response.status_code == 200)

    def test_home_route_returns_200(self):
        """."""
        response = self.client.get(reverse_lazy("home"))
        self.assertTrue(response.status_code == 200)

    def test_home_view_returns_data_dict(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue("data" in response.context)
        self.assertIsInstance(response.context['data'], dict)

    def test_home_view_has_offense_title_and_count_in_dict(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy('home'))
        violence_data = response.context['data']['violence']
        violence_ct = Consequence.objects.filter(
            offense_cat__contains='violence'
        ).count()
        violence_title = dict(OFFENSE_CATEGORIES)['violence']
        self.assertTrue(violence_data['title'] == violence_title)
        self.assertTrue(violence_data['count'] == violence_ct)

    def test_home_view_not_showing_none_misc(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy('home'))
        data = response.context['data']
        self.assertFalse('---' in data)
        self.assertFalse('misc' in data)

    def test_home_route_uses_proper_template(self):
        """."""
        response = self.client.get(reverse_lazy('home'))
        self.assertTemplateUsed(response, 'front-end/home.html')


class ResultsViewTests(TestCase):
    """Tests of the results view."""

    def setUp(self):
        """Setup for the results view tests."""
        self.client = Client()
        self.request_builder = RequestFactory()

    @mock.patch(
        "collateral_consequence.scraper.get_data",
        return_value=NY_DATA
    )
    def fill_db(self, get_data):
        """Fill the database with consequences."""
        ingest_rows("NY")

    def test_get_results_route_is_200(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "felony": True
        })
        self.assertTrue(response.status_code == 200)

    def test_get_results_felony_returns_proper_count(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "felony": True
        })
        felony_ct = Consequence.objects.filter(
            state="NY",
            duration__in=["perm", "spec"],
            offense_cat__contains="felony"
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], felony_ct)

    def test_get_results_misdemeanor_returns_proper_count(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "misdem": True
        })
        misdem_ct = Consequence.objects.filter(
            state="NY",
            duration__in=["perm", "spec"],
            offense_cat__contains="misdemeanor"
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], misdem_ct)

    def test_get_results_misdem_and_felony_returns_proper_count(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "misdem": True, "felony": True
        })
        qry = Q(offense_cat__contains="felony")
        qry |= Q(offense_cat__contains='misdemeanor')
        qry |= Q(offense_cat__contains="Any offense")
        consqs_ct = Consequence.objects.filter(
            qry,
            state="NY",
            duration__in=["perm", "spec"],
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], consqs_ct)

    def test_get_results_offense_returns_proper_count(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "offense": ["weapons"]
        })
        qry = Q(offense_cat__contains="weapons")
        qry |= Q(offense_cat__contains="Any offense")
        consqs_ct = Consequence.objects.filter(
            qry,
            state="NY",
            duration__in=["perm", "spec"],
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], consqs_ct)

    def test_get_results_many_offense_returns_proper_count(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "offense": ["weapons", "violence"]
        })
        qry = Q(offense_cat__contains="weapons")
        qry |= Q(offense_cat__contains="violence")
        qry |= Q(offense_cat__contains="Any offense")
        consqs_ct = Consequence.objects.filter(
            qry,
            state="NY",
            duration__in=["perm", "spec"],
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], consqs_ct)

    def test_get_results_bad_offense_ignores(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "offense": ["fluffiness"]
        })
        qry = Q(offense_cat__contains="Any offense")
        consqs_ct = Consequence.objects.filter(
            qry,
            state="NY",
            duration__in=["perm", "spec"],
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], consqs_ct)

    def test_get_results_bad_good_offense_ignores_bad(self):
        """."""
        self.fill_db()
        response = self.client.get(reverse_lazy(
            "results", kwargs={"state": "NY"}), {
            "offense": ["fluffiness", "weapons"]
        })
        qry = Q(offense_cat__contains="weapons")
        qry |= Q(offense_cat__contains="Any offense")
        consqs_ct = Consequence.objects.filter(
            qry,
            state="NY",
            duration__in=["perm", "spec"],
        ).exclude(consequence_type__contains="bkg").count()
        self.assertEqual(response.context["count"], consqs_ct)
