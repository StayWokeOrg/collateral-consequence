"""Warehouse for utility functions for views."""
from collateral_consequence import scraper
from crimes.models import Consequence
from crimes.processing import process_spreadsheet

from django.db.models import Q
from django.db.transaction import TransactionManagementError
from django.db.utils import DataError


def filter_by_offenses(query_manager, offenses):
    """Filter consequences down by offense(s)."""
    if offenses:
        complex_query = Q(offense_cat__contains=offenses[0])
        if len(offenses) > 1:
            for offense in offenses[1:]:
                complex_query |= Q(offense_cat__contains=offense)

        return query_manager.filter(complex_query)
    return query_manager


def ingest_rows(state):
    """Given a dataframe, input new data into the database."""
    if not Consequence.objects.filter(state=state).count():
        data = scraper.get_data(scraper.make_url(state))
        processed_data = process_spreadsheet(data)
        duration_dict = {
            'Specific Term': "spec",
            'N/A (background check, general relief)': "bkg",
            'Conditional': "cond",
            'Permanent/Unspecified': "perm",
            'None': 'none'
        }

        all_offenses = []
        all_consequence_cats = []
        all_consequence_types = []
        for idx in range(len(processed_data)):
            citation = processed_data.iloc[idx]

            cols = [
                "Parsed Offense Category",
                "Parsed Consequence Category",
                "Parsed Consequence Type"
            ]
            offenses = [item.replace(",", "") for item in citation[cols[0]]]
            categories = [item.replace(",", "") for item in citation[cols[1]]]
            con_types = [item.replace(",", "") for item in citation[cols[2]]]

            all_offenses.extend(offenses)
            all_consequence_cats.extend(categories)
            all_consequence_types.extend(con_types)

            new_consq = Consequence(
                title=citation.Title,
                citation=citation.Citation,
                state=state,
                consequence_details=citation["Consequence Details"],
                duration=duration_dict[citation["Duration Category"]],
                duration_desc=citation["Duration Description"],
                offense_cat=offenses,
                consequence_cat=categories,
                consequence_type=con_types
            )
            try:
                new_consq.save()
            except (DataError, TransactionManagementError):  # pragma: no cover
                print("Broke at: ", citation.Title)
                print(
                    "Consequence details: ",
                    len(citation["Consequence Details"])
                )
                print("Duration: ", len(citation["Duration Category"]))
                print(
                    "Duration Description: ",
                    len(citation["Duration Description"])
                )
                print("Offense list: ", len(offenses))
                print("Consequence categories list: ", len(categories))
                print(
                    "Consequence type list: {}\n\n".format(len(con_types))
                )
                pass
