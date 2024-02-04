import random
import time
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
import os

# Constants
URL = 'https://www.cityu.edu.hk/pg/taught-postgraduate-programmes/list'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL
school_name = BASE_PATH.split('_')[-1]


def download_html(url):
    session = requests.Session()

    headers = {
        'authority': 'masters.smu.edu.sg',
        # 'method': 'GET',
        # 'path': '/programmes',
        'scheme': 'https',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Cookie': "visid_incap_2480916=8lCch3j7SNu4VgB+SKTQiEuUoGUAAAAAQUIPAAAAAACcl+XTIFHXXamSIk6cel8B; _gcl_au=1.1.330651366.1705022542; _fbp=fb.2.1705022542064.1143887163; __qca=P0-878428341-1705022541950; marker_id_642aa66c7b103f77417a7647=6129d65c-bc37-410d-a35f-7f3eac7f501a; OptanonAlertBoxClosed=2024-01-12T01:22:28.914Z; visid_incap_823419=8nU0TZVtS6CdweSli+6AMLmJsGUAAAAAQUIPAAAAAACEq0qQyy8bbM7lYbUft/L1; _hjSessionUser_2727825=eyJpZCI6IjRmZGVmNWY2LWIwNDgtNTNkMC1iMWNlLWUwZjQ0NjIxOTFkYyIsImNyZWF0ZWQiOjE3MDYwNjg0MTE2NTUsImV4aXN0aW5nIjp0cnVlfQ==; visid_incap_2480929=FQFME0/DR3iZcE3pce67FbuJsGUAAAAAQUIPAAAAAADhDXqzoBs+WjxoviqW0bgR; visid_incap_2480912=lbb3LWCVQeqiIo31bbFVtbuJsGUAAAAAQUIPAAAAAAAIM0plISft/uclR5lk7dBs; visid_incap_2045174=auUMrrYYTVS8Xg0NSLi2MLuJsGUAAAAAQUIPAAAAAACtEdiKC5DtBa2BEvQuIm90; _ga_WGRFPYWXN0=GS1.1.1706068411.1.1.1706068433.38.0.0; incap_ses_1700_2480916=B6XEWGzGsh7S2SMamJ2XFw4Es2UAAAAAbd4ShGdlhsSlU8xWI9wWuA==; _gid=GA1.3.1759554424.1706230801; _clck=1ebtmuv%7C2%7Cfiq%7C0%7C1472; _ga_4Y66YGQ0FG=GS1.1.1706230801.3.1.1706231793.31.0.0; _ga_SKE4KV2FV9=GS1.1.1706230801.3.1.1706231793.31.0.0; _ga=GA1.1.51990194.1705022542; _ga_N1G7RZ7VSB=GS1.3.1706230801.3.1.1706231793.32.0.0; cto_bundle=ythz7l9VWjR0dCUyRnRycWh3Y1dsNnlLSUgyVFdUWXI5N3N5TGlSbk4wQ090eGFhJTJGblg1UVhYNTRoOFcybmUlMkY3QU5OJTJCc2dnbVRQczJRUTF4a2pRRmFWVnF3MjAyNVQwMnolMkI2TjlNTCUyQmNqJTJGNkwxRXE0YkM3QXYlMkZ5VEhzekFWczRjdW1GbHdQVk9zeEtrZ2VxbyUyQnBHRzdLSDg5UG9MdG9GRHZiUDJZTDRoOGtBVHZEUk5RdnN5ZWVBbnl3dWo1ZTJ1MCUyRkZUajl3WXoyY2VYdjJLaTF5TDc3ZXFTblElM0QlM0Q; _clsk=li6gc5%7C1706231793646%7C7%7C1%7Ce.clarity.ms%2Fcollect; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jan+25+2024+20%3A16%3A35+GMT-0500+(Eastern+Standard+Time)&version=6.17.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&geolocation=US%3BPA&AwaitingReconsent=false",
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    # 随机延迟
    time.sleep(random.uniform(1, 5))

    response = session.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# def download_html(url):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     return response.text


def parse_html(html):
    classes = ['CB', 'CENG', 'CH', 'CSCI', 'VM', 'SM', 'DS', 'E2', 'FL']
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr', class_=classes)
    programmes_data = []
    for row in rows:
        columns = row.find_all('td')
        if columns:
            prog_code = columns[0].get_text(strip=True)
            prog_title = columns[1].get_text(strip=True).split('\n')[0]
            local_deadline = columns[3].get_text(strip=True)
            non_local_deadline = columns[4].get_text(strip=True)
            deadline = "local: " + local_deadline + "\n" + "non-local: " + non_local_deadline + "\n"
            programmes_data.append([prog_code, prog_title, deadline])
    return pd.DataFrame(programmes_data, columns=['Code', 'Programme', 'Deadline'])


def compare_and_notify(old_data, new_data):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
        log_file.write(f"Function called at {datetime.now()}\n")

    if old_data.empty:
        print("No old data to compare with. Saving new data.")
        return

    # Check for any differences
    if not old_data.equals(new_data):
        print("Data differences detected...")

        changes_detected = []
        new_rows_detected = []
        deleted_rows_detected = []

        for index, new_row in new_data.iterrows():
            # Check if the row exists in the old data
            old_row = old_data.loc[old_data['Programme'] == new_row['Programme']]

            # If the row exists, check for deadline changes
            if not old_row.empty:
                if old_row['Deadline'].values[0] != new_row['Deadline']:
                    changes_detected.append({
                        'Programme': new_row['Programme'],
                        'Old Deadline': old_row['Deadline'].values[0],
                        'New Deadline': new_row['Deadline']
                    })
            else:
                # If the row does not exist in old data, it's a new addition
                new_rows_detected.append(new_row)

        # Check for deleted programmes
        for index, old_row in old_data.iterrows():
            new_row = new_data.loc[new_data['Programme'] == old_row['Programme']]
            if new_row.empty:
                deleted_rows_detected.append(old_row)

        # Preparing email content
        subject = "Changes Detected in Taught Programmes"
        body = ""

        if changes_detected:
            body += "Deadline changes detected:\n\n"
            for change in changes_detected:
                body += (f"School: {school_name}, Programme: {change['Programme']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

        if new_rows_detected:
            body += "New programmes added:\n\n"
            for new_row in new_rows_detected:
                body += (f"School: {school_name}, Programme: {new_row['Programme']}\n"
                         f"Deadline: {new_row['Deadline']}\n\n")

        if deleted_rows_detected:
            body += "Programmes deleted:\n\n"
            for del_row in deleted_rows_detected:
                body += f"School: {school_name}, Programme: {del_row['Programme']}\n\n"

        # Sending the email if there are any changes
        if changes_detected or new_rows_detected or deleted_rows_detected:
            send_email(subject, body, recipient_email)
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"),
                      "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected.")

    else:
        print("No changes detected in the data content.")

def main():
    # Download HTML
    new_html = download_html(URL)

    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_EXCEL):
        old_data = pd.read_excel(SAVE_PATH_EXCEL)
    else:
        old_data = pd.DataFrame()

    # Compare and notify
    compare_and_notify(old_data, new_data)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_EXCEL, index=False)


if __name__ == "__main__":
    main()
