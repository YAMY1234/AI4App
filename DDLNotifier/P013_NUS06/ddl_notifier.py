from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P016_EDUMO.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

school_name = BASE_PATH.split('_')[-1]
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')  # CSV file with current program data

recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for notifications
# recipient_email = 'yamy12344@gmail.com'  # Replace with your actual email for notifications
SAVE_PATH_OLD_XLSX = 'program_deadlines.xlsx'  # Save path for the old Excel file
SAVE_PATH_NEW_XLSX = 'program_deadlines.xlsx'  # Save path for the new Excel file
SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, SAVE_PATH_OLD_XLSX)  # Save path for the HTML
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, SAVE_PATH_NEW_XLSX)  # Save path for the CSV
log_file = os.path.join(BASE_PATH, "notification_log.txt")

constant_deadline = None


def get_constant_deadline(url="https://law1a.nus.edu.sg/admissions/app_periods_forms.html"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for 4xx and 5xx errors
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    deadlines = {}

    # Find the specific table containing the deadlines. Adjust the selector as needed.
    tables = soup.find_all('table')
    if not tables:
        print("No tables found on the page")
        return None

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:  # Check if row has enough columns
                program_cell = cells[0]
                application_period = cells[1].get_text(strip=True)
                submission_deadline = cells[2].get_text(strip=True)

                # Extract program names and match them with their deadlines
                links = program_cell.find_all('a')
                for link in links:
                    program_name = link.get_text(strip=True)
                    deadlines[program_name] = {
                        "Application Period": application_period,
                        "Submission Deadline": submission_deadline
                    }

    return deadlines


def get_deadline(url):
    # 发送GET请求
    return constant_deadline

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)

def main():
    global constant_deadline
    constant_deadline = get_constant_deadline()
    # Read current program data
    current_program_data = get_current_programs_and_urls()

    # Prepare a list to collect new data
    new_data_list = []

    # Get the new deadline data
    for index, row in current_program_data.iterrows():
        program_name = row['ProgramName']
        url_link = row['URL Link']
        try:
            deadline_text = get_deadline(url_link)
            new_data_list.append({'Programme': program_name, 'Deadline': deadline_text})
            print(f"Retrieved deadlines for {program_name}, deadline_text: {deadline_text}")
        except Exception as e:
            print(f"Error retrieving deadlines for {program_name}: {e}")

    # Create a new DataFrame from the list of new data
    new_data = pd.DataFrame(new_data_list)

    # Read old data if it exists
    old_data = pd.DataFrame()
    if os.path.exists(SAVE_PATH_OLD_XLSX):
        old_data = pd.read_excel(SAVE_PATH_OLD_XLSX)

    # If old data is not empty, compare and notify
    if not old_data.empty:
        compare_and_notify(old_data, new_data, log_file, school_name)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_NEW_XLSX, index=False)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()
