from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email  # Replace with your actual email module
from DDLNotifier.P006_HKBU.program_url_crawler import crawl

school_name = "HKBU"

# Constants
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')  # CSV file with current program data

# recipient_email = 'yamy12344@gmail.com'  # Replace with your actual email for notifications
recipient_email = 'suki@itongzhuo.com' # Replace with your actual email for notifications
SAVE_PATH_OLD_XLSX = 'program_deadlines.xlsx'  # Save path for the old Excel file
SAVE_PATH_NEW_XLSX = 'program_deadlines.xlsx'  # Save path for the new Excel file
SAVE_PATH_TMP_XLSX = 'program_deadlines_temp.xlsx'  # Save path for the new Excel file
SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, SAVE_PATH_OLD_XLSX)  # Save path for the HTML
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, SAVE_PATH_NEW_XLSX)  # Save path for the CSV
SAVE_PATH_TMP_XLSX = os.path.join(BASE_PATH, SAVE_PATH_TMP_XLSX)  # Save path for the CSV


def get_deadline(url):
    # 发送GET请求
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找“Study Mode”标签
    study_mode_tag = soup.find('span', class_="icon-title-txt__title", text='Study Mode')
    if study_mode_tag:
        # 检查是否包含“Full-time”
        if 'Full-time' in study_mode_tag.parent.get_text():
            # 存在“Full-time”时，继续查找截止日期标签
            deadline_tag = soup.find('span', class_="icon-title-txt__title", text='Cut Off Date')
            if deadline_tag and deadline_tag.next_sibling:
                return deadline_tag.next_sibling.get_text(strip=True)
            return 'Deadline not found'
    return 'No Full-time program found'



def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)


def compare_and_notify(old_data, new_data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
        log_file.write(f"Function called at {datetime.now()}\n")

    if old_data.empty:
        print("No old data to compare with. Skipping comparison.")
        return False

    changes_detected = False
    new_programs_detected = False
    print("Comparing old and new data...")
    for index, new_row in new_data.iterrows():
        program_name = new_row['ProgramName']
        old_row = old_data[old_data['ProgramName'] == program_name]

        if not old_row.empty:
            # Check if there is a change in 'DeadlineText'
            if old_row['DeadlineText'].values[0] != new_row['DeadlineText']:
                changes_detected = True
                subject = f"Change Detected in Deadline for {program_name}"
                body = (f"School: HKUST, Program: {program_name}\n"
                        f"Old Deadline: {old_row['DeadlineText'].values[0]}\n"
                        f"New Deadline: {new_row['DeadlineText']}\n\n")
                send_email(subject, body, recipient_email)  # Implement this function in your email module
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                    log_file.write(f"Email sent: {subject} | {body}\n")
        else:
            # If the program does not exist in old data, it's a new addition
            new_programs_detected = True
            subject = f"School: {school_name}, New Program Added: {program_name}"
            body = (f"New Program: {program_name}\n"
                    f"Deadline: {new_row['DeadlineText']}\n\n")
            send_email(subject, body, recipient_email)  # Implement this function in your email module
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")

    return changes_detected or new_programs_detected


def main():
    crawl()
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
            new_data_list.append({'ProgramName': program_name, 'DeadlineText': deadline_text})
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
        changes_detected = compare_and_notify(old_data, new_data)
        if changes_detected:
            print("Changes detected and notifications sent.")
        else:
            print("No changes detected.")

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_NEW_XLSX, index=False)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()