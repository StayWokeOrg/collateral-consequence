"""Scripts for processing data inputs."""


def process_spreadsheet(sheet):
    """Take a given spreadsheet and parse/reduce columns."""
    keep_columns = [
        "Citation", "Title", "Consequence Category", "Consequence Details",
        "Consequence Type", "Duration Category", "Triggering Offense Category",
        "Duration Description", "Additional Triggering Offenses",
        "Additional Offense Details"
    ]
    sheet = sheet.copy()[keep_columns]
    sheet.fillna("None", inplace=True)
    for column in keep_columns:
        sheet = strip_column(sheet, column)

    categories = [
        ("Parsed Offense Category", "Triggering Offense Category"),
        ("Parsed Additional Offenses", "Additional Triggering Offenses")
    ]
    for cat in categories:
        sheet[cat[0]] = sheet[cat[1]].map(lambda x: parse_offense_column(x))

    sheet = remove_non_offenses(sheet)
    sheet = sheet.reindex(range(len(sheet)))
    return sheet


def parse_offense_column(offense_str):
    """Split a string of offenses into a list of items."""
    if offense_str is not "None":
        output = offense_str.replace("#", "")
        output = output.split(";")
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
    return data[data[column].map(lambda x: "N/A" not in x)]
