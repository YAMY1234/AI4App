from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
import pandas as pd
import os
from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
URL = 'https://wis.ntu.edu.sg/webexe/owa/coal_main.notice'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL

school_name = BASE_PATH.split('_')[-1]

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")

def download_html(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    headers = None
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_html(html):
    # 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')

    # 用于存储提取的数据
    programmes_data = []

    # 遍历每一行
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 5:
            # 提取所需数据
            program_name = columns[2].get_text(strip=True)
            opening_date = columns[3].get_text(strip=True)
            closing_date = columns[4].get_text(strip=True)
            deadline = f"{opening_date} to {closing_date}"

            # 添加到列表
            programmes_data.append([program_name, deadline])

    # 创建 DataFrame
    return pd.DataFrame(programmes_data, columns=['Programme', 'Deadline'])

def main():
    # Download HTML
    print("Downloading HTML...")
    new_html = download_html(URL)

    print("Parsing HTML...")
    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_EXCEL):
        old_data = pd.read_excel(SAVE_PATH_EXCEL)
    else:
        old_data = pd.DataFrame()

    print("Comparing old and new data...")
    # Compare and notify
    compare_and_notify(old_data, new_data, log_file, school_name)

    new_data.to_excel(SAVE_PATH_EXCEL, index=False)


if __name__ == "__main__":
    main()
