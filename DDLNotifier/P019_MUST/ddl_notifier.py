from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P019_MUST.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify

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

def get_constant_deadline():
    url = "https://www.must.edu.mo/cn/sgs/admission/oas/important-dates"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找包含“报名期”文本的<strong>标签
    registration_period_heading = soup.find('strong', text='报名期')

    # 如果找到了这个标签，继续查找下一个<tr>标签
    if registration_period_heading:
        tr = registration_period_heading.find_parent('tr')
        if tr:
            # 在<tr>标签中查找包含日期的<td>标签
            date_cells = tr.find_all('td')
            dates = [date_cell.text.strip() for date_cell in date_cells[1:4]]

            # 拼接成一个字符串返回
            return ', '.join(dates)

    return "日期未找到"




def get_deadline(url):
    return constant_deadline

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)


def main():
    global constant_deadline
    constant_deadline = get_constant_deadline()
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
