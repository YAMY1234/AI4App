from datetime import datetime
import time
import random

import requests
from bs4 import BeautifulSoup
from DDLNotifier.config import CONFIG
import pandas as pd
import os
from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
URL = 'https://fass.nus.edu.sg/prospective-students/graduate/coursework-programmes/application-process-gradcoursework/'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL

school_name = BASE_PATH.split('_')[-1]
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")


def download_html(url):
    session = requests.Session()

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Cookie": "visid_incap_2431398=SZ6bQTaURkCblUv1sBBvxqRl+mUAAAAAQUIPAAAAAABOors9ILWCvnWCTyRY2VN+; nlbi_2431398=MN5MTX2xMkjzPS33YtCAhAAAAACelH6MY7nuAk12AYS3gLLR; incap_ses_1350_2431398=5HeSMUXXuWVuAdAL4Cq8EqZl+mUAAAAASrtNkkzY4oUv3DO7AL1omg==; _ga=GA1.1.34324038.1710908840; visid_incap_1750112=b/7BY2A/RjqChmUzd3geTqdl+mUAAAAAQUIPAAAAAAAEaaEDlgeatEYknoYo0lnF; incap_ses_1350_1750112=XDsvW5JNpxOQBNAL4Cq8Eqdl+mUAAAAA3IBuxth1kEHaMzKHLGELnA==; _ga_DWXTFQZLLP=GS1.1.1710908839.1.1.1710909842.0.0.0",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # 随机延迟
    time.sleep(random.uniform(1, 5))

    response = session.get(url, headers=headers)
    response.raise_for_status()
    return response.text

from bs4 import BeautifulSoup
import pandas as pd

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    programmes_data = []

    # Skip the first row as it contains header information
    rows = soup.find_all('tr')[1:]

    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 3:  # Rows that start a new intake period
            intake = columns[0].get_text(" ", strip=True)
            application_period = columns[1].get_text(" ", strip=True)
            programmes = columns[2].get_text("\n", strip=True).split('\n')
        elif len(columns) == 2:  # Continuing rows for the same intake
            application_period = columns[0].get_text(" ", strip=True)
            programmes = columns[1].get_text("\n", strip=True).split('\n')

        for programme in programmes:
            programmes_data.append([programme, f"{intake}: {application_period}"])

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
