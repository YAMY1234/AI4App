from datetime import datetime

import pandas as pd
import requests
import sys
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
# from DDLNotifier.P013_NUS03.program_url_crawler import crawl

parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

from program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify
from DDLNotifier.utils.get_request_header import WebScraper

# Constants
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

school_name = BASE_PATH.split('_')[-1]
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')  # CSV file with current program data

recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for notifications
SAVE_PATH_OLD_XLSX = 'program_deadlines.xlsx'  # Save path for the old Excel file
SAVE_PATH_NEW_XLSX = 'program_deadlines.xlsx'  # Save path for the new Excel file
SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, SAVE_PATH_OLD_XLSX)  # Save path for the HTML
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, SAVE_PATH_NEW_XLSX)  # Save path for the CSV
log_file = os.path.join(BASE_PATH, "notification_log.txt")

constant_deadline = None
webScraper = WebScraper()

def get_deadline(url):
    # 发送GET请求
    url = url[-1] == '/' and url[:-1] or url
    response_text = webScraper.get_html(url + "/application")
    soup = BeautifulSoup(response_text, "html.parser")

    # 查找包含"Programme Briefing"文本的<h4>标签
    programme_briefing_h4 = soup.find("h4", string="Programme Briefing\n")
    if not programme_briefing_h4:
        programme_briefing_h4 = soup.find("h4", string="Programme Briefing")

    if programme_briefing_h4:
        # 找到紧接着的<div>标签
        next_div = programme_briefing_h4.find_next("div")
        if next_div:
            # 提取<div>标签里的所有文本，并且用换行符链接
            texts = next_div.get_text(separator="\n", strip=True)
            return texts
    return "Deadline information not found."

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)

def main():
    # get_deadline("https://www.comp.nus.edu.sg/programmes/pg/phdis/")
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
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()
