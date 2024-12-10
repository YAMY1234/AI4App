from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P001_HKU.program_url_crawler import crawl
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
    """
    获取申请截止日期信息，并在存在申请链接时附加相关信息。

    参数:
        url (str): 目标网页的URL。

    返回:
        str: 提取的申请截止日期信息，或错误消息。
    """
    # 初始化超时参数
    timeout_duration = 5  # 初始超时时间为5秒
    cnt = 3  # 最大重试次数

    while cnt > 0:
        try:
            # 发送GET请求，禁用SSL验证（根据需要）
            response = requests.get(url, verify=False, timeout=timeout_duration)
            response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError
            break  # 请求成功，跳出循环
        except requests.Timeout:
            # 处理请求超时
            cnt -= 1
            timeout_duration += 5  # 每次超时后增加超时时间
            print(f"请求超时。增加超时时间到 {timeout_duration} 秒... 还剩 {cnt} 次尝试。")
        except requests.HTTPError as http_err:
            # 处理HTTP错误
            print(f"HTTP错误发生: {http_err}")
            cnt = 0  # 不再重试
        except requests.RequestException as req_err:
            # 处理其他请求相关错误
            print(f"请求错误发生: {req_err}")
            cnt = 0  # 不再重试

    if cnt == 0:
        # 请求失败，记录错误日志
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")
        with open(log_path, "a", encoding='utf-8') as log_file:
            log_file.write("ERROR !! Request timed out after 3 attempts\n")
        return "请求超时"

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 定位到包含申请截止日期的部分
    tab_content = soup.find("div", class_="tab-content")
    if not tab_content:
        return "找不到tab-content部分"

    # 找到所有高亮项
    highlights = tab_content.find_all("div", class_="highlights-item")
    if not highlights:
        return "找不到highlights-item元素"

    application_deadline = None

    # 遍历高亮项，找到“Application Deadline”部分
    for item in highlights:
        title_div = item.find("div", class_="highlights-item-title")
        description_div = item.find("div", class_="highlights-item-description")

        if title_div and description_div:
            title_text = title_div.get_text(strip=True)
            if title_text == "Application Deadline":
                # 提取截止日期描述文本
                application_deadline = description_div.get_text(separator=" ", strip=True)
                break

    if not application_deadline:
        return "找不到申请截止日期信息"

    # 查找页面底部的<a>标签（例如“Apply Now”按钮）
    apply_now_link = tab_content.find("a", class_="btn-apply")
    if apply_now_link and apply_now_link.get("href"):
        link_text = apply_now_link.get_text(strip=True)
        link_href = apply_now_link["href"]
        # 将链接信息附加到截止日期文本中
        application_deadline += f" ({link_text}: \"{link_href}\")"

    return application_deadline


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
