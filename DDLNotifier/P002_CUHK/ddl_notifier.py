from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from DDLNotifier.utils.compare_and_notify import compare_and_notify
from DDLNotifier.config import CONFIG

# Constants
URL = 'https://www.gs.cuhk.edu.hk/admissions/admissions/application-deadline'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_XLSX = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for testing

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")

school_name = BASE_PATH.split('_')[-1]

def download_html(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all divs containing the Taught Programmes deadlines
    right_cols = soup.find_all('div', class_='_50 application-deadline-tb-col content-tb right')

    taught_programmes_data = []

    # Extracting each programme's deadlines from all the right columns
    for right_col in right_cols:
        # The first 'div' with class 'application-deadline-tb-txt' contains the programme name
        programme_name_divs = right_col.find_all('div', class_='application-deadline-tb-txt')
        for programme_name_div in programme_name_divs:
            programme_name = programme_name_div.text.strip()
            if programme_name == 'Taught Programmes':
                continue
            programme_name = programme_name.split('\n')[0].strip()
            # Find all 'p' tags within this programme_name_div div to get the deadlines
            deadline_ps = programme_name_div.find_all('p')
            ddls = []
            for deadline_p in deadline_ps:
                deadline_info = deadline_p.get_text(strip=True)
                if deadline_info:  # Ensure that the extracted text is not empty
                    ddls.append(deadline_info)
            taught_programmes_data.append([programme_name, '\n'.join(ddls)])

    return pd.DataFrame(taught_programmes_data, columns=['Programme', 'Deadline'])

def main():
    # Download HTML
    new_html = download_html(URL)

    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_XLSX):
        old_data = pd.read_excel(SAVE_PATH_XLSX)
    else:
        old_data = pd.DataFrame()

    # Compare and notify
    compare_and_notify(old_data, new_data, log_file, school_name)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_XLSX, index=False)


# Run the main function
if __name__ == "__main__":
    main()
