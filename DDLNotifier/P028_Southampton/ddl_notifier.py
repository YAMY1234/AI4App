import time
from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P028_Southampton.program_url_crawler import crawl
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
SAVE_PATH_NEW_XLSX_WITH_TIMESTAMP = os.path.join(BASE_PATH, f"program_deadlines-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx")

log_file = os.path.join(BASE_PATH, "notification_log.txt")

'''
export OPENSSL_CONF=/etc/ssl/openssl.cnf
python /root/AI4App/DDLNotifier/notifier_routine.py
'''


def get_deadline(url):
    max_retries = 3  # 最大重试次数
    retry_delay = 2  # 每次重试之间的延迟时间（秒）

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            response = requests.get(url + "#apply", timeout=10)
            if response.status_code != 200:
                return f"Error fetching the page: {response.status_code}"

            soup = BeautifulSoup(response.text, 'html.parser')
            print("Fetched the page successfully")

            deadlines_text = []

            # First attempt: Look for paragraphs directly under 'Application deadlines' with spans
            deadlines_heading = soup.find("h3", string=lambda text: "application deadlines" in text.lower() if text else False)
            if deadlines_heading:
                print("Found 'Application deadlines' heading")
                next_p = deadlines_heading.find_next("p")
                while next_p and next_p.name == "p":
                    span_texts = [span.text.strip() for span in next_p.find_all("span")]
                    if span_texts:
                        deadlines_text.extend(span_texts)
                    else:
                        deadlines_text.append(next_p.text.strip())
                    next_p = next_p.find_next_sibling("p")

            # Second attempt: Look for the section 'Application deadlines' directly
            if deadlines_heading:
                next_ul = deadlines_heading.find_next("ul")
                if next_ul:
                    deadline_items = next_ul.find_all("li")
                    if deadline_items:
                        deadlines_text.extend(item.text.strip() for item in deadline_items)
                print("Empty 'ul' found, proceeding to next attempt")

            if deadlines_text:
                return " | ".join(deadlines_text)

            # Third attempt: Look for any paragraphs or lists under 'How to apply'
            apply_section = soup.find("div", id="apply")
            if apply_section:
                print("Found 'apply' section")
                paragraphs = apply_section.find_all("p")
                for p in paragraphs:
                    if "application deadline" in p.text.lower():
                        deadlines_text.append(p.text.strip())
                # Additionally check for lists under apply_section
                lists = apply_section.find_all("ul")
                for ul in lists:
                    for li in ul.find_all("li"):
                        if "application deadline" in li.text.lower():
                            deadlines_text.append(li.text.strip())

            if deadlines_text:
                return " | ".join(deadlines_text)

            return "Deadline section not found"
        except Exception as e:
            print(f"Error during attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:  # 等待一段时间后重试
                time.sleep(retry_delay)
            else:
                return f"Error processing the page after {max_retries} attempts: {str(e)}"

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)

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

    # 保存    programs-当前时间戳.xlsx
    new_data.to_excel(f"program_deadlines-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx", index=False)

    # 检查当前文件夹下时间戳后缀为3天之前的文件，如果存在则删除
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        print(file)
        if file.startswith("program_deadlines-") and file.endswith(".xlsx"):
            file_time = pd.Timestamp(file.split("-")[1].split(".")[0])
            if pd.Timestamp.now() - file_time >= pd.Timedelta(days=3):
                os.remove(file)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()

