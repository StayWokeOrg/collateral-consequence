"""Warehouse for utility functions for views."""
from collateral_consequence import scraper
from collateral_consequence.settings import BASE_DIR
from crimes.models import Consequence
from crimes.processing import process_spreadsheet

from django.db.models import Q
from django.db.transaction import TransactionManagementError
from django.db.utils import DataError

import os

DURATION_DICT = {
    'Specific Term': "spec",
    'N/A (background check, general relief)': "bkg",
    'Conditional': "cond",
    'Permanent/Unspecified': "perm",
    'None': 'none'
}


def filter_by_offenses(query_manager, offenses):
    """Filter consequences down by offense(s)."""
    if offenses:
        complex_query = Q(offense_cat__contains=offenses[0])
        if len(offenses) > 1:
            for offense in offenses[1:]:
                complex_query |= Q(offense_cat__contains=offense)

        return query_manager.filter(complex_query)
    return query_manager


def ingest_from_remote(state):
    """Given a state, scrape and input new data into the database."""
    if not Consequence.objects.filter(state=state).count():
        data = scraper.get_data(scraper.make_url(state))
        processed_data = process_spreadsheet(data)
        ingest_rows(processed_data, state)


def handle_uploaded_file(infile, state):
    """Save file to disk then reread file as dataframe."""
    fname = infile.name
    filepath = os.path.join(BASE_DIR, "tmp", fname)
    with open(filepath, "wb+") as outfile:
        for chunk in infile.chunks():
            outfile.write(chunk)

    read_as_df = scraper.get_data(filepath)
    os.remove(filepath)
    processed_data = process_spreadsheet(read_as_df)
    ingest_rows(processed_data, state)


def ingest_rows(data_file, state):
    """Input actual data into the database from file."""
    for idx in range(len(data_file)):
        citation = data_file.iloc[idx]
        offenses, categories, con_types = parse_multi_input_columns(citation)
        save_new_consequence(citation, offenses, categories, con_types, state)


def parse_multi_input_columns(citation):
    """Parse out individual columns from data with multiple inputs."""
    cols = [
        "Parsed Offense Category",
        "Parsed Consequence Category",
        "Parsed Consequence Type"
    ]
    offenses = [item.replace(",", "") for item in citation[cols[0]]]
    categories = [item.replace(",", "") for item in citation[cols[1]]]
    consequence_types = [item.replace(",", "") for item in citation[cols[2]]]
    return offenses, categories, consequence_types


def save_new_consequence(citation, offenses, categories, con_types, state):
    """."""
    new_consq = Consequence(
        title=citation.Title,
        citation=citation.Citation,
        state=state,
        consequence_details=citation["Consequence Details"],
        duration=DURATION_DICT[citation["Duration Category"]],
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
