from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P035_Nottingham.program_url_crawler import crawl
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


constant_deadline = None

def get_constant_deadline(url="https://www.nottingham.ac.uk/pgstudy/how-to-apply/apply-online.aspx"):
    # 发送GET请求并获取网页内容
    timeout_duration = 5
    cnt = 3  # 更正错误：原先 cnt += 1 应该是 cnt -= 1
    while cnt > 0:
        try:
            response = requests.get(url, verify=False, timeout=timeout_duration)
            break
        except requests.Timeout:
            cnt -= 1
            timeout_duration += 5  # 增加超时时间
            print(f"Timeout. Increasing timeout duration to {timeout_duration} seconds...")
            continue

    if cnt == 0:
        # 打印错误日志到本地文件
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")
        with open(log_path, "a") as log_file:
            log_file.write("ERROR !! Request timed out after 3 attempts\n")
        return "Request timed out"

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 定位到包含特定标题的表格部分
    table_body = soup.find("tbody")
    if table_body:
        rows = table_body.find_all("tr")
        deadlines = []
        # 遍历表格中的每一行，提取国际学生截止日期信息
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:  # 确保有足够的单元格来提取数据
                # 提取国际学生截止日期的单元格
                international_deadline = cells[2].text.strip()
                deadlines.append(international_deadline)
        return "\n".join(deadlines)
    else:
        return "Deadline information not found"

def get_deadline(url):
    return constant_deadline

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)


def main():
    crawl()
    constant_deadline = get_constant_deadline()
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
