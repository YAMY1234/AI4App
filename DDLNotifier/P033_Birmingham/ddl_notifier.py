from datetime import datetime
import time

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P033_Birmingham.program_url_crawler import crawl
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


def get_deadline_old(url):
    try:
        response = requests.get(url, verify=False)
    except Exception as e:
        return f"Error fetching URL: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # 尝试从包含 fact-boxes 的区块中查找 deadline 信息
    fact_sections = soup.find_all(lambda tag: tag.name in ["section", "div"] and
                                              tag.has_attr("class") and
                                              any("fact-boxes" in cls for cls in tag["class"]))

    for section in fact_sections:
        # 在区块中查找 article 标签，包含 card-fact 的可能就是我们需要的信息
        articles = section.find_all(lambda tag: tag.name == "article" and
                                                tag.has_attr("class") and
                                                any("card-fact" in cls for cls in tag["class"]))
        for article in articles:
            # 获取描述信息并检查是否包含"deadline"关键词（忽略大小写）
            desc = article.find(lambda tag: tag.has_attr("class") and
                                            any("card-fact__description" in cls for cls in tag["class"]))
            if desc and re.search(r'\bdeadline\b', desc.get_text(), re.IGNORECASE):
                stat = article.find(lambda tag: tag.has_attr("class") and
                                                any("card-fact__stat" in cls for cls in tag["class"]))
                if stat:
                    return stat.get_text(strip=True)

    # 如果没有从 fact-boxes 中找到，则尝试查找标题中包含 "Application deadlines" 的h2/h3标签
    deadline_heading = soup.find(lambda tag: tag.name in ["h2", "h3"] and
                                             "Application deadlines" in tag.get_text())
    if deadline_heading:
        next_p = deadline_heading.find_next("p")
        if next_p:
            return next_p.get_text(strip=True)

    # 兜底方法：查找 "How To Apply" 相关信息
    apply_tags = soup.find_all("h2", class_="accordion__title")
    for tag in apply_tags:
        if "How To Apply" in tag.get_text(strip=True):
            content = []
            current_tag = tag.find_next()
            while current_tag and current_tag.name not in ["h2", "a"]:
                if current_tag.name == "p":
                    content.append(current_tag.get_text(strip=True))
                current_tag = current_tag.find_next()
            if content:
                return "\n".join(content)

    return "No deadline information found"


def get_deadline(url, retries=3, delay=5):
    SEARCH_RANGE = 300  # 从关键词后往后抓多少字符
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=30, verify=False)
            html_text = response.text
            # return html_text  # 或继续你的后续逻辑
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return f"Error fetching URL after {retries} attempts: {e}"

    # 1. 找到 "internationalApplicationProcessComposer" 的位置
    marker = '"internationalApplicationProcessComposer"'
    index = html_text.find(marker)
    if index == -1:
        return "No 'internationalApplicationProcessComposer' keyword found in page."

    # 2. 取从该位置开始, 往后 SEARCH_RANGE 个字符的片段
    end_index = index + SEARCH_RANGE
    snippet = html_text[index:end_index]

    # 3. 用一个宽松的日期正则, 匹配 "12 May 2025" 之类的格式 (日 + 英文月份 + 20xx)
    #    允许 1~2位日, 再加空白, 再加 3~10位英文字母(比如 January ~ September), 再加空白, 再加 20开头的4位年
    date_pattern = re.compile(r"(\d{1,2}\s+[A-Za-z]{3,10}\s+20\d{2})")

    match = date_pattern.search(snippet)
    if match:
        return match.group(1).strip()
    else:
        return "No date found near 'internationalApplicationProcessComposer'."


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
