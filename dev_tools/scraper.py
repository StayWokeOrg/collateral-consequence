"""Run this script to locally download xls files from NICCC."""
from urllib import request
import os

states = {
    'NY': '35',
    'VI': '1002',
    'NV': '31',
    'NJ': '33',
    'NH': '32',
    'VA': '47',
    'VT': '1',
    'NM': '34',
    'NC': '36',
    'ND': '37',
    'NE': '30',
    'FL': '14',
    'WA': '48',
    'KS': '20',
    'WI': '50',
    'OR': '40',
    'KY': '21',
    'OH': '38',  # <-- got a bad gateway
    'OK': '39',
    'FED': '1000',
    'WV': '49',
    'WY': '51',
    'CO': '3',
    'CA': '10',  # <-- got a bad gateway
    'GA': '15',
    'RI': '42',
    'CT': '11',
    'PA': '41',
    'TN': '44',
    'TX': '45',
    'HI': '16',
    'PR': '1003',
    'LA': '22',
    'SD': '43',
    'DC': '13',
    'DE': '12',
    'SC': '5',
    'IA': '4',
    'ID': '17',
    'UT': '46',
    'IN': '19',
    'IL': '18',
    'AK': '7',
    'ME': '23',
    'MD': '24',
    'MA': '25',
    'AL': '6',
    'MO': '28',
    'MN': '2',
    'MI': '26',
    'AZ': '8',
    'MT': '29',
    'MS': '27',
    'AR': '9'
}


def make_url(state_abrv):
    """Set up a URL For a given state."""
    base_url = 'https://niccc.csgjusticecenter.org/export_search_results/?keyword=&new=&jurisdictions%5B%5D={}&multiselect={}&duration=&excluded_words='
    return base_url.format(states[state_abrv], states[state_abrv])


def main():
    """Run this from the command line."""
    for s in states:
        print("Fetching {}...".format(s))
        fname = "scraped_files/consq_{}.xls".format(s)
        if fname.split("/")[-1] not in os.listdir("scraped_files"):
            resp = request.urlopen(make_url(s))
            with open(fname, 'wb') as out:
                out.write(resp.read())
        else:
            print("{} already obtained. Skipping...".format(s))

if __name__ == "__main__":
    main()
