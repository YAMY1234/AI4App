from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P026_Bristol.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify, update_error_urls_with_old_data
import time

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


def get_deadline(url, max_retries=3, backoff_factor=1):
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(url, verify=False, timeout=10)  # 设置超时时间
            response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找 'Application deadline' dt 标签，然后导航到其 dd 标签
            deadline_dt = soup.find("dt", string="Application deadline")
            if deadline_dt:
                deadline_dd = deadline_dt.find_next("dd")
                if deadline_dd:
                    # 从下一个 p 标签中提取文本，包含截止日期详情
                    deadline_p = deadline_dd.find_next("p")
                    if deadline_p:
                        return deadline_p.get_text(strip=True).replace("Overseas applicants:",
                                                                       "Overseas:").replace(
                            "Home applicants:", "Home:")
            return "Deadline section not found"
        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                wait = backoff_factor * (2 ** (attempt - 1))  # 指数退避策略
                print(f"尝试 {attempt} 失败，等待 {wait} 秒后重试...")
                time.sleep(wait)
            else:
                return f"Error processing the page: after {max_retries} attempts: {e}"


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
        new_data = update_error_urls_with_old_data(new_data=new_data, old_data=old_data)
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
