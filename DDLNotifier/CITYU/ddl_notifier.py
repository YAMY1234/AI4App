from bs4 import BeautifulSoup
import requests
import pandas as pd
from DDLNotifier.email_sender import send_email
import os

# Constants
URL = 'https://www.cityu.edu.hk/pg/taught-postgraduate-programmes/list'
SAVE_PATH_HTML = 'previous_page.html'  # Save path for the HTML
SAVE_PATH_CSV = 'taught_programmes_data.csv'  # Save path for the CSV
recipient_email = 'yamy12344@gmail.com'  # Replace with your actual email for testing

def download_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr', class_='CB')
    programmes_data = []
    for row in rows:
        columns = row.find_all('td')
        if columns:
            prog_code = columns[0].get_text(strip=True)
            prog_title = columns[1].get_text(strip=True).split('\n')[0]
            local_deadline = columns[3].get_text(strip=True)
            non_local_deadline = columns[4].get_text(strip=True)
            deadline = "local: " + local_deadline + "\n" + "non-local: " + non_local_deadline + "\n"
            programmes_data.append([prog_code, prog_title, deadline])
    return pd.DataFrame(programmes_data, columns=['Code', 'Programme Title', 'Deadline'])


# Function to compare old and new programme data and notify if there are differences
def compare_and_notify(old_data, new_data, recipient_email=recipient_email):
    if old_data.empty:
        print("No old data to compare with. Saving new data.")
        return

    # Check for any differences
    if not old_data.equals(new_data):
        print("Data differences detected...")

        changes_detected = []
        new_rows_detected = []

        # Convert the DataFrame to a dictionary for easier comparison
        old_data_dict = old_data.set_index('Programme Title').to_dict(orient='index')

        for index, new_row in new_data.iterrows():
            programme_title = new_row['Programme Title']
            deadline = new_row['Deadline']

            # Check if the row exists in the old data
            old_row = old_data_dict.get(programme_title)

            # If the row exists, check for deadline changes
            if old_row and old_row['Deadline'] != deadline:
                changes_detected.append({
                    'Programme Title': programme_title,
                    'Old Deadline': old_row['Deadline'],
                    'New Deadline': deadline
                })
            elif not old_row:
                # If the row does not exist in old data, it's a new addition
                new_rows_detected.append(new_row)

        # Preparing email content
        subject = "Changes Detected in Taught Programmes"
        body = ""

        if changes_detected:
            body += "Deadline changes detected:\n\n"
            for change in changes_detected:
                body += (f"Programme: {change['Programme Title']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

        if new_rows_detected:
            body += "New programmes added:\n\n"
            for new_row in new_rows_detected:
                body += (f"Programme: {new_row['Programme Title']}\n"
                         f"Deadline: {new_row['Deadline']}\n\n")

        # Sending the email if there are any changes
        if changes_detected or new_rows_detected:
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
    if os.path.exists(SAVE_PATH_CSV):
        old_data = pd.read_csv(SAVE_PATH_CSV)
    else:
        old_data = pd.DataFrame()

    # Compare and notify
    compare_and_notify(old_data, new_data)

    # Save the new data for future comparisons
    new_data.to_csv(SAVE_PATH_CSV, index=False)

if __name__ == "__main__":
    main()
