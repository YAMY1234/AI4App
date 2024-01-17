from datetime import datetime
import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
import pandas as pd
import os

# Constants
URL = 'https://admissions.hku.hk/tpg/programme-list'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_HTML = os.path.join(BASE_PATH, 'previous_page.html')  # Save path for the HTML
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL


def download_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all tables with the specified class attributes
    tables = soup.find_all('table', {'class': 'table table-bordered table-striped'})

    programme_data = []

    for table in tables:
        rows = table.find_all('tr')

        # Extracting headers from the first table only, assuming all tables have the same structure
        headers = ["Programme", "Deadline", "Apply"]
        if not programme_data:
            headers = [header.get_text().strip() for header in rows[0].find_all('th')]
            headers = headers[:1] + headers[2:4]  # Adjusting the headers to exclude the 'Download Documents' column

        # Extracting rows
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:  # Ensure there are enough columns
                programme_name = cols[0].get_text().strip()
                deadline_info = cols[2].get_text().strip()
                apply_info = cols[3].get_text().strip()

                # Check for full-time option
                if 'Full Time' in apply_info:
                    programme_data.append([programme_name, deadline_info, apply_info])

    return pd.DataFrame(programme_data, columns=headers)

def compare_and_notify(old_data, new_data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
        log_file.write(f"Function called at {datetime.now()}\n")

    if old_data.empty:
        print("No old data to compare with. Saving new data.")
        return

    if not old_data.equals(new_data):
        print("Data differences detected...")

        changes_detected = []
        new_programmes_detected = []

        for programme in new_data['Programme'].unique():
            print(old_data['Programme'])
            old_row = old_data[old_data['Programme'] == programme]
            new_row = new_data[new_data['Programme'] == programme]

            # Check if the programme exists in the old data
            if not old_row.empty:
                # If there's a change in the 'Deadline' column for a 'Full Time' programme
                if not old_row.equals(new_row) and 'Full Time' in new_row['Apply'].values[0]:
                    old_deadline = old_row['Deadline'].values[0]
                    new_deadline = new_row['Deadline'].values[0]
                    changes_detected.append({
                        'Programme': programme,
                        'Old Deadline': old_deadline,
                        'New Deadline': new_deadline
                    })
            else:
                # If the programme does not exist in old data, it's a new addition
                if 'Full Time' in new_row['Apply'].values[0]:
                    new_programmes_detected.append({
                        'Programme': programme,
                        'Deadline': new_row['Deadline'].values[0]
                    })

        # Preparing email content
        subject = "Changes Detected in Programmes"
        body = ""

        if changes_detected:
            body += "Deadline changes detected:\n\n"
            for change in changes_detected:
                body += (f"School: HKU, Programme: {change['Programme']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

        if new_programmes_detected:
            body += "New programmes added:\n\n"
            for new_programme in new_programmes_detected:
                body += (f"School: HKU, Programme: {new_programme['Programme']}\n"
                         f"Deadline: {new_programme['Deadline']}\n\n")
        # Sending the email if there are any changes
        if changes_detected or new_programmes_detected:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")
            send_email(subject, body, recipient_email)
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected in the data table with 'Full Time' in Apply column.")
    else:
        print("No changes detected in the data content.")


def main():
    # Download HTML
    new_html = download_html(URL)

    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_EXCEL):
        old_data = pd.read_excel(SAVE_PATH_EXCEL)
    else:
        old_data = pd.DataFrame()

    # Compare and notify
    compare_and_notify(old_data, new_data)

    new_data.to_excel(SAVE_PATH_EXCEL, index=False)

if __name__ == '__main__':
    main()
