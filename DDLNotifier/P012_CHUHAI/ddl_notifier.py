from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P012_CHUHAI.program_url_crawler import crawl
import re

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

# def get_deadline(url):
#     # 发送GET请求
#     response = requests.get(url, verify=False)
#     response.encoding = 'utf-8'
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     # 使用正则表达式进行灵活匹配
#     start_tag = soup.find('h3', text=re.compile('Application Periods|Application Deadlines|報名日期'))
#     end_tag = soup.find('h3', text=re.compile('How to Apply|報名方法|2024/25學年度學費'))
#
#     if start_tag and end_tag:
#         content = []
#         current_tag = start_tag.next_sibling
#         while current_tag and current_tag != end_tag:
#             if current_tag.name and current_tag.name not in ['h3', 'script', 'style']:
#                 content.append(current_tag.get_text(strip=True))
#             current_tag = current_tag.next_sibling
#
#         return '\n'.join(content)
#     else:
#         if "%20" in url:
#             ret_val = get_deadline(url.replace("%20", "-").lower())
#             return ret_val
#         return 'Application Periods or How to Apply section not found'


START_PAT = re.compile(
    r"(Application\s*(Periods|Deadlines)|報名日期|報名時間|申請時段)",
    re.I
)
# 结束锚点可以列多一点，越靠后越准确
END_PAT = re.compile(
    r"(How\s*to\s*Apply|申請方法|Admissions? Brochure|Additional Information|學費|Tuition)",
    re.I
)

def get_deadline(url: str, *, verify_ssl: bool = True, timeout: int = 10) -> str:
    r = requests.get(url, verify=verify_ssl, timeout=timeout)
    r.encoding = r.apparent_encoding or "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    # —— 1. 找到包含起始关键字的“任何”节点 ——
    start_node = soup.find(string=lambda s: s and START_PAT.search(s))
    if not start_node:
        if "%20" in url:
            return get_deadline(url.replace("%20", "-").lower())
        return "Application Period section not found"

    # —— 2. 从该节点所属 tag 开始，顺序遍历所有后续节点，直到碰到 END_PAT 或文档末尾 ——
    lines = []
    for element in start_node.find_parent().next_elements:
        # A. 触发终止条件
        if getattr(element, "get_text", None):
            text = element.get_text(" ", strip=True)
            if END_PAT.search(text):
                break
        # B. 过滤掉无意义节点
        if element.name in {"script", "style"}:
            continue
        if isinstance(element, str):      # NavigableString
            continue
        # C. 把可见文本收集起来，保留换行
        text = element.get_text("\n", strip=True)
        if text:
            lines.append(text)

    # —— 3. 去重（保持原顺序） ——
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return "\n".join(unique_lines) or "No date info found"

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
    main()
