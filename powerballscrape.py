"""
powerballscraper.py:

The first Powerball game was April 22, 1992. Unfortunately the Powerball website only holds data from November 1, 1997.
This simple script allows us to scrape all results up to current day quickly into "winners.csv". This file is rewritten
every time the script is run.
"""
__author__ = "Felajan"
__copyright__ = "Copyright 2022, Felajan"
__credits__ = ["Felajan",]
__version__ = "1.0.1"
__maintainer__ = "Felajan"
__email__ = "felajan@protonmail.com"
__status__ = "Production"
__created_date__ = "2018-03-19"

import requests
import csv
import sys
from datetime import date

# keys for the csv file we will be creating
fieldnames = ['first_number', 'second_number', 'third_number', 'fourth_number', 'fifth_number',
              'powerball', 'multiplier', 'draw date']
# powerball url requires time, this will be the max time we use at the end of our queries, includes a leading space for the sake of the url
spacetimemax = " 23:59:59"

def resultParser(results):
    results = results
    parsed_results = {f: '' for f in fieldnames}
    unparsed_winning_numbers = results['field_winning_numbers'].rsplit(sep=',')
    count = 0
    for x in unparsed_winning_numbers:
        parsed_results[fieldnames[count]] = x
        count += 1
        # print("The count is {}".format(count))
    parsed_results['multiplier'] = results['field_multiplier']
    parsed_results['draw date'] = results['field_draw_date']
    return parsed_results

def newRequestLoop():
    with open('winners.csv', 'w', newline='') as csvfile:
        print("[*] CSV file open.")

        base_url = "https://www.powerball.com/api/v1/numbers/powerball?_format=json&min=2000-01-01%2000:00:00&max="
        max_date = date.today().isoformat()
        split_date = max_date.split(sep="-")
        full_url = base_url + max_date + spacetimemax
        print(full_url)

        try:
            numberwriter = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
        except Exception as err:
            print("Unable to open DictWriter.")
            print("Error: {}".format(err))
            csvfile.close()
            sys.exit(0)

        print("[*] Writing the header row.")
        numberwriter.writeheader()

        # start new loop here!!!
        loop_count = 0
        while True:
            r = requests.get(full_url)
            print("Status code is {}".format(r.status_code))
            if r.status_code == 200 and loop_count == 0:
                number_of_games = len(r.json())
                print("[*] Printing {} results.".format(number_of_games))
                for game in r.json():
                    print("[*] Parsing resuilts...")
                    game = resultParser(game)
                    print("[*] Writing this dictonary:\n{}".format(game))
                    numberwriter.writerow(game)
                # now reconfigure to pull next set of numbers and continue loop
                max_date = r.json()[number_of_games - 1]['field_draw_date'].split(sep='-')
                max_date = date(int(max_date[0]), int(max_date[1]), int(max_date[2])).isoformat()
                full_url = base_url + max_date + spacetimemax
                loop_count += 1
            elif r.status_code == 200 and loop_count >= 1:
                # subtract one since we are skipping the first result, which is already on the csv file
                number_of_games = len(r.json()) - 1
                print("[*] Printing {} results.".format(number_of_games))
                for count in r.json()[1:]:
                    print("[*] Parsing results...")
                    count = resultParser(count)
                    print("[*] Writing this dictionary: {}".format(count))
                    numberwriter.writerow(count)
                # check if we have reached the end of the list
                # powerball website returns results 100 at a time
                # break loop
                if number_of_games <= 98:
                    break
                # now reconfigure full_url and loop
                max_date = r.json()[number_of_games - 1]['field_draw_date'].split(sep='-')
                max_date = date(int(max_date[0]), int(max_date[1]), int(max_date[2])).isoformat()
                full_url = base_url + max_date + spacetimemax
                loop_count += 1
            else:
                print("[*] Invalid link.")
                csvfile.close()
                sys.exit(0)
    csvfile.close()
    sys.exit(0)

def main():
    newRequestLoop()

main()
