from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
from DDLNotifier.utils.compare_and_notify import compare_and_notify
import pandas as pd
import os

# Constants
URL = 'https://gs.hksyu.edu/en/Prospective-Students/Application'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")

school_name = BASE_PATH.split('_')[-1]


def download_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    programmes_data = []

    for row in rows[1:]:  # 跳过表头
        columns = row.find_all('td')
        if len(columns) >= 3:  # 确保有足够的列
            programme_name = columns[0].get_text(strip=True)
            deadlines = columns[2].get_text(strip=True)
            programmes_data.append([programme_name, deadlines])

    return pd.DataFrame(programmes_data, columns=['Programme', 'Deadline'])


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
