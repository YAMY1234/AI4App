from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P022_Edinburgh.program_url_crawler import crawl
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
log_file = os.path.join(BASE_PATH, "notification_log.txt")


def get_deadline(url):
    # 发送GET请求并获取网页内容
    timeout_duration = 5
    cnt = 30
    while cnt > 0:
        try:
            response = requests.get(url, verify=False, timeout=timeout_duration)
            break
        except requests.Timeout:
            cnt += 1
            print(f"Timeout. Increasing timeout duration to {timeout_duration} seconds...")
            continue
    if cnt == 0:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
            log_file.write(f"ERROR !! cnt == 10 \n")
        return "Request timed out"
    # try:
    #     # 发送GET请求并获取网页内容，设置超时时间
    #     response = requests.get(url, verify=False, timeout=timeout_duration)
    # except requests.Timeout:
    #     # 如果请求超时，返回一个错误信息
    #     return "Request timed out"

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 查找包含“Application deadlines”链接的<div class="panel-heading">
    # deadline_heading = soup.find("div", class_="panel-heading",
    #                              string=lambda text: "Application deadlines" in text if text else False)
    # deadline_heading = soup.find("a", string="Application deadlines")
    deadline_heading = soup.find(lambda tag: tag.name == "a" and "Application deadlines" in tag.text)

    if deadline_heading:
        # 找到该标题后的第一个<div>，其中包含截止日期信息
        deadline_div = deadline_heading.find_next("div", class_="panel-collapse collapse")
        if deadline_div:
            # 提取该<div>内的所有文本
            texts = deadline_div.find_all(text=True)
            return ' '.join(text.strip() for text in texts)
        else:
            return "Application deadlines section not found"
    else:
        # 如果没有找到相应标题，返回特定字符串
        return "Application deadlines section not found"

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
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    # print(get_deadline("https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/view&edition=2024&id=634"))

    main()
