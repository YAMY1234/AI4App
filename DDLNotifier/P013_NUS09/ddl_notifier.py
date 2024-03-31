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
URL = 'https://sph.nus.edu.sg/education/mph/how-to-apply/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL

school_name = BASE_PATH.split('_')[-1]
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")

webScrapper = WebScraper()

def download_html(url):
    response_text = webScrapper.get_html(url)
    return response_text


months = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

def parse_html(html):
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize a string to hold the concatenated deadline information
    deadline_info = ""

    # Find all 'p' elements
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        # Convert paragraph to lowercase for case-insensitive matching
        text = p.get_text(strip=True).lower()

        # Check if the paragraph contains any month names or relevant words
        if any(word in text for word in ['open', 'close', 'application'] + months):
            # Add this deadline information to the accumulator string
            deadline_info += p.get_text(strip=True).replace('\n', ' ') + " "

    # Since the program is known, no need to dynamically extract it
    program_name = "Master of Public Health"

    # Create a DataFrame with a single row for the program and its accumulated deadline information
    df = pd.DataFrame([[program_name, deadline_info.strip()]], columns=['Programme', 'Deadline'])

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
