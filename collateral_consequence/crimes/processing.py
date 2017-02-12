"""Scripts for processing data inputs."""
import os
import pandas as pd


def process_spreadsheet(sheet):
    """Take a given spreadsheet and parse/reduce columns."""
    keep_columns = [
        "Citation", "Title", "Consequence Category", "Consequence Details",
        "Consequence Type", "Duration Category", "Triggering Offense Category",
        "Duration Description", "Additional Triggering Offenses",
        "Additional Offense Details"
    ]
    sheet = reduce_columns(sheet, keep_columns)
    sheet.fillna("None", inplace=True)
    for column in keep_columns:
        sheet = strip_column(sheet, column)

    categories = [
        (
            "Parsed Offense Category",
            "Triggering Offense Category",
            parse_offense_column,
            ";"
        ),
        (
            "Parsed Additional Offenses",
            "Additional Triggering Offenses",
            parse_offense_column,
            ";"
        ),
        (
            "Parsed Consequence Category",
            "Consequence Category",
            parse_offense_column,
            ";"
        ),
        (
            "Parsed Consequence Type",
            "Consequence Type",
            parse_offense_column,
            "; "
        )
    ]
    for cat in categories:
        sheet[cat[0]] = sheet[cat[1]].map(lambda x: cat[2](x, cat[3]))

    sheet = remove_non_offenses(sheet)
    return sheet


def reduce_columns(data, columns):
    """Keep only those columns that we need for our work."""
    return data.copy()[columns]


def parse_offense_column(offense_str, split_str=";"):
    """Split a string of offenses into a list of items."""
    if offense_str != "None":
        output = offense_str.replace("#", "")
        output = output.split(split_str)
        output = [string.strip() for string in output]
    else:
        output = [None]
    return output


def strip_column(data, column_name):
    """Take a column and remove leading/trailing whitespace."""
    data[column_name] = data[column_name].map(lambda x: x.strip())
    return data


def remove_non_offenses(data):
    """No need for rows that aren't offenses."""
    column = "Triggering Offense Category"
    return data[data[column].map(lambda x: "N/A" not in x and "None" not in x)]


if __name__ == "__main__":  # pragma: no cover
    cats = []
    consequence_cats = []
    unparsed_cats = []
    consequence_type = []
    unparsed_types = []
    duration_cat = []
    duration_desc = []
    additional_offenses = []

    sheets_dir = '/Users/Nick/Documents/staywoke/collateral-consequence/dev_tools/scraped_files'
    sheets = [pd.read_excel(os.path.join(sheets_dir, f)) for f in os.listdir(sheets_dir) if f.endswith(".xls")]
    for sheet in sheets:
        data_sheet = process_spreadsheet(sheet)
        for cat in data_sheet["Parsed Offense Category"]:
            cats.extend(cat)
        for cat in data_sheet["Parsed Consequence Category"]:
            consequence_cats.extend(cat)
        for cat in data_sheet["Consequence Category"]:
            unparsed_cats.append(cat)
        for the_type in data_sheet["Parsed Consequence Type"]:
            consequence_type.extend(the_type)
        for the_type in data_sheet["Consequence Type"]:
            unparsed_types.append(the_type)
        for offense in data_sheet["Parsed Additional Offenses"]:
            additional_offenses.extend(offense)
        for cat in data_sheet["Duration Category"]:
            duration_cat.append(cat)
        for desc in data_sheet["Duration Description"]:
            duration_desc.append(desc)

    print("Offense Categories: ", set(cats), end="\n\n")
    print("Consequence Categories: ", set(consequence_cats), end="\n\n")
    print("Consequence Types: ", set(consequence_type), end="\n\n")
    print("Duration Categories: ", set(duration_cat), end="\n\n")
