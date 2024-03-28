from datetime import datetime
import time
import random

import requests
from bs4 import BeautifulSoup
from DDLNotifier.config import CONFIG
import pandas as pd
import os
from DDLNotifier.utils.compare_and_notify import compare_and_notify
from DDLNotifier.utils.get_request_header import WebScraper

# Constants
URL = 'https://cde.nus.edu.sg/graduate/graduate-programmes-by-coursework/application-period/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL

school_name = BASE_PATH.split('_')[-1]
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")

webScrapper = WebScraper()

def download_html(url):
    response_text = webScrapper.get_html(url)
    return response_text


from bs4 import BeautifulSoup
import pandas as pd

def parse_html(html):
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize a list to hold the parsed data
    parsed_data = []

    # Find all 'tr' elements
    rows = soup.find_all('tr')

    for row in rows:
        # For each 'tr', find all 'td' tags
        tds = row.find_all('td')

        # Check if there are exactly three 'td' tags
        if len(tds) == 3:
            # Extract the program name from the first 'td' tag
            program_name = tds[0].find('a').text.strip() if tds[0].find(
                'a') else ''
            if program_name == '':
                continue

            # Extract the texts for the deadline from the second and third 'td' tags
            deadline = tds[1].text.strip() + "\n" + tds[2].text.strip()

            # Append the extracted data to the list
            parsed_data.append([program_name, deadline])

    # Convert the list to a DataFrame
    df = pd.DataFrame(parsed_data, columns=['Programme', 'Deadline'])

    return df


def main():
    # Download HTML
    print("Downloading HTML...")
    new_html = download_html(URL)

    print("Parsing HTML...")
    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_EXCEL):
        old_data = pd.read_excel(SAVE_PATH_EXCEL)
    else:
        old_data = pd.DataFrame()

    print("Comparing old and new data...")
    # Compare and notify
    compare_and_notify(old_data, new_data, log_file, school_name)

    new_data.to_excel(SAVE_PATH_EXCEL, index=False)


if __name__ == "__main__":
    main()
