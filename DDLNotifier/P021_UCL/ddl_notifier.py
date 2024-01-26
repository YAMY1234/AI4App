from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P021_UCL.program_url_crawler import crawl

# Constants
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

school_name = BASE_PATH.split('_')[-1]
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')  # CSV file with current program data

recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for notifications
# recipient_email = 'yamy12344@gmail.com'  # Replace with your actual email for notifications
SAVE_PATH_OLD_XLSX = 'program_deadlines.xlsx'  # Save path for the old Excel file
SAVE_PATH_NEW_XLSX = 'program_deadlines.xlsx'  # Save path for the new Excel file
SAVE_PATH_TMP_XLSX = 'program_deadlines_temp.xlsx'  # Save path for the new Excel file
SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, SAVE_PATH_OLD_XLSX)  # Save path for the HTML
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, SAVE_PATH_NEW_XLSX)  # Save path for the CSV
SAVE_PATH_TMP_XLSX = os.path.join(BASE_PATH, SAVE_PATH_TMP_XLSX)  # Save path for the CSV

'''
export OPENSSL_CONF=/etc/ssl/openssl.cnf
python /root/AI4App/DDLNotifier/notifier_routine.py
'''


def get_deadline(url):
    # 发送GET请求并获取网页内容
    response = requests.get(url, verify=False)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 检查“Study mode”后是否有“Full-time”
    study_mode_tag = soup.find("h5", string="Study mode")
    if study_mode_tag and "Full-time" in study_mode_tag.find_next().text.strip():
        # 如果有，找到“Applications accepted”后的第一个div并提取所有文本
        applications_accepted_tag = soup.find("h5", string="Applications accepted")
        if applications_accepted_tag:
            next_div = applications_accepted_tag.find_next("div")
            texts = next_div.find_all(text=True)
            return ' '.join(text.strip() for text in texts)
    else:
        # 如果没有，返回特定字符串
        return "part time do not need to consider"


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
    deleted_programs_detected = False
    print("Comparing old and new data...")
    for index, new_row in new_data.iterrows():
        program_name = new_row['ProgramName']
        old_row = old_data[old_data['ProgramName'] == program_name]

        if not old_row.empty:
            # Check if there is a change in 'DeadlineText'
            if old_row['DeadlineText'].values[0] != new_row['DeadlineText']:
                changes_detected = True
                subject = f"Change Detected in Deadline for {program_name}"
                body = (f"School: {school_name}, Program: {program_name}\n"
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
    
    # New code for detecting deleted programs
    for index, old_row in old_data.iterrows():
        program_name = old_row['ProgramName']
        new_row = new_data[new_data['ProgramName'] == program_name]
        
        if new_row.empty:
            deleted_programs_detected = True
            subject = f"School: {school_name}, Program Deleted: {program_name}"
            body = (f"Deleted Program: {program_name}\n\n")
            send_email(subject, body, recipient_email)  # Implement this function in your email module
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")

    return changes_detected or new_programs_detected or deleted_programs_detected


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
