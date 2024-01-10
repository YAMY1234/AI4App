from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
import pandas as pd
import os

# Constants
URL = 'https://admission.hsu.edu.hk/taught-postgraduate-admissions/programme-information/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_HTML = os.path.join(BASE_PATH, 'previous_page.html')  # Save path for the HTML
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = 'suki@itongzhuo.com'
# recipient_email = 'yamy12344@gmail.com'

school_name = 'HSU'


def download_html(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    headers = None
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 找到所有包含项目信息的行
    rows = soup.find_all('tr')

    programmes_data = []

    # 遍历每一行提取项目名称和截止日期
    for row in rows:
        # 找到项目名称所在的列
        name_col = row.find('td', class_='column-1')
        if name_col and name_col.a:
            programme_name = name_col.a.text.strip()

            continue_flag = False
            for program in programmes_data:
                if programme_name == program[0]:
                    continue_flag = True
            if continue_flag:
                continue

            # 找到截止日期所在的列
            deadline_col_2 = row.find('td', class_='column-2')
            deadline_col_3 = row.find('td', class_='column-3')
            deadlines = []

            if deadline_col_2:
                deadlines.append(deadline_col_2.get_text(strip=True))
            if deadline_col_3:
                deadlines.append(deadline_col_3.get_text(strip=True))

            programmes_data.append([programme_name, ' and '.join(deadlines)])

    return pd.DataFrame(programmes_data, columns=['Programme', 'Deadline'])


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
                body += (f"School: CUHK, Programme: {change['Programme']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

        if new_rows_detected:
            body += "New programmes added:\n\n"
            for new_row in new_rows_detected:
                body += (f"School: {school_name}, Programme: {new_row['Programme']}\n"
                         f"Deadline: {new_row['Deadline']}\n\n")

        # Sending the email if there are any changes
        if changes_detected or new_rows_detected:
            send_email(subject, body, recipient_email)
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected.")

    else:
        print("No changes detected in the data content.")


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
    compare_and_notify(old_data, new_data)

    new_data.to_excel(SAVE_PATH_EXCEL, index=False)


if __name__ == "__main__":
    main()