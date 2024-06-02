from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
from DDLNotifier.utils.compare_and_notify import compare_and_notify
import pandas as pd
import os

# Constants
URL = 'https://www.eduhk.hk/acadprog/postgrad/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")
recipient_email = CONFIG.RECIPEINT_EMAIL
# recipient_email = 'yamy12344@gmail.com'

school_name = BASE_PATH.split('_')[-1]


def download_html(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    headers = None
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    programmes_data = []

    # 找到所有的 'faq_in_text' div元素
    for div in soup.find_all('div', class_='faq_in_text'):
        # 获取程序名称
        title = div.find(class_='title').get_text(strip=True)

        # 获取截止日期
        deadline = div.find(class_='editor').get_text(strip=True)

        programmes_data.append([title, deadline])

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
