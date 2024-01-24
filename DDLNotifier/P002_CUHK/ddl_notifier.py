from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG

# Constants
URL = 'https://www.gs.cuhk.edu.hk/admissions/admissions/application-deadline'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_XLSX = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for testing

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
        programme_name_div = right_col.find('div', class_='application-deadline-tb-txt')
        if programme_name_div:
            programme_name = programme_name_div.text.strip()
            if programme_name == 'Taught Programmes':
                continue
            programme_name = programme_name.split('\n')[0].strip()
            # Find all 'p' tags within this right_col div to get the deadlines
            deadline_ps = right_col.find_all('p')
            ddls = []
            for deadline_p in deadline_ps:
                deadline_info = deadline_p.get_text(strip=True)
                if deadline_info:  # Ensure that the extracted text is not empty
                    ddls.append(deadline_info)
            taught_programmes_data.append([programme_name, '\n'.join(ddls)])

    return pd.DataFrame(taught_programmes_data, columns=['Programme', 'Deadline'])

def compare_and_notify(old_data, new_data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
        log_file.write(f"Function called at {datetime.now()}\n")

    if old_data.empty:
        print("No old data to compare with. Saving new data.")
        return

    # Check for any differences
    if not old_data.equals(new_data):
        print("Data differences detected...")

        changes_detected = []
        new_rows_detected = []

        for index, new_row in new_data.iterrows():
            # Check if the row exists in the old data
            old_row = old_data.loc[old_data['Programme'] == new_row['Programme']]

            # If the row exists, check for deadline changes
            if not old_row.empty:
                if old_row['Deadline'].values[0] != new_row['Deadline']:
                    changes_detected.append({
                        'Programme': new_row['Programme'],
                        'Old Deadline': old_row['Deadline'].values[0],
                        'New Deadline': new_row['Deadline']
                    })
            else:
                # If the row does not exist in old data, it's a new addition
                new_rows_detected.append(new_row)

        # Preparing email content
        subject = "Changes Detected in Taught Programmes"
        body = ""

        if changes_detected:
            body += "Deadline changes detected:\n\n"
            for change in changes_detected:
                body += (f"School: {school_name}, Programme: {change['Programme']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

        if new_rows_detected:
            body += "New programmes added:\n\n"
            for new_row in new_rows_detected:
                body += (f"School: CUHK, Programme: {new_row['Programme']}\n"
                         f"Deadline: {new_row['Deadline']}\n\n")

        # Sending the email if there are any changes
        if changes_detected or new_rows_detected:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")
            send_email(subject, body, recipient_email)
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected.")

    else:
        print("No changes detected in the data content.")


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
    compare_and_notify(old_data, new_data)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_XLSX, index=False)


# Run the main function
if __name__ == "__main__":
    main()
