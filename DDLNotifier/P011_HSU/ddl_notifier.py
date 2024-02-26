from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
import pandas as pd
import os

from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
URL = 'https://admission.hsu.edu.hk/taught-postgraduate-admissions/programme-information/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL
# recipient_email = 'yamy12344@gmail.com'

school_name = BASE_PATH.split('_')[-1]

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")


def download_html(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    headers = None
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 找到所有包含项目信息的行
    rows = soup.find_all('tr')

    programmes_data = []

    # 遍历每一行提取项目名称和截止日期
    for row in rows:
        # 找到项目名称所在的列
        name_col = row.find('td', class_='column-1')
        if name_col and name_col.a:
            programme_name = name_col.a.text.strip()

            continue_flag = False
            for program in programmes_data:
                if programme_name == program[0]:
                    continue_flag = True
            if continue_flag:
                continue

            # 找到截止日期所在的列
            deadline_col_2 = row.find('td', class_='column-2')
            deadline_col_3 = row.find('td', class_='column-3')
            deadlines = ["begin:"]

            if deadline_col_2:
                deadlines.append(deadline_col_2.get_text(strip=True))
            if deadline_col_3:
                deadlines.append(deadline_col_3.get_text(strip=True))

            programmes_data.append([programme_name, ' and '.join(deadlines)])

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
