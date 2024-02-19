import os
import json
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
from html import unescape
import re

# Constants
URL = 'https://www.polyu.edu.hk/study/pg/taught-postgraduate'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
recipient_email = CONFIG.RECIPEINT_EMAIL
school_name = BASE_PATH.split('_')[-1]

def download_html_old(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def download_html(url):
    # 构建请求的 URL
    url = 'https://www.polyu.edu.hk/study/views/ajax?_wrapper_format=drupal_ajax'

    # 设置请求头（Headers）
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        # ... 添加任何其他必要的头部信息
    }

    # 设置请求的正文数据（Payload）
    payload = {
        'pg_programmes_semester_term_value': '2516',
        'pg_programmes_faculty_school_target_id_verf': 'All',
        'combine': '',
        'view_name': 'pg_programmes',
        'view_display_id': 'programme_listing',
        'view_args': '',
        'view_path': '/node/91',
        'view_base_path': '',
        'view_dom_id': 'f2ccfb6a4d5d4058990775a2b0b169ed3d899a8e817cca54d022dffade6be84c',
        'pager_element': '0',
        '_drupal_ajax': '1',
        'ajax_page_state[theme]': 'polyu_theme',
        'ajax_page_state[theme_token]': '',
        # ... 添加任何其他必要的正文信息
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=payload)

    # 检查响应状态码
    if response.status_code == 200:
        # 打印响应的内容
        print(response.text)
    else:
        print('Failed to retrieve data:', response.status_code)
    return response.text

def parse_html(html):
    # Parse the JSON string
    data = json.loads(html)
    # Assuming the HTML content is in the last 'data' element
    html_content = unescape(data[-2]['data'])

    # Now that we have the HTML, we can use BeautifulSoup to parse it
    soup = BeautifulSoup(html_content, 'html.parser')

    # soup = BeautifulSoup(html, 'html.parser')
    programme_blocks = soup.find_all('div', class_='views-row')
    programmes_data = []

    for block in programme_blocks:
        study_mode_and_duration = block.find('div', class_='study-mode-and-duration')
        # Skip part-time programmes
        if not ('Full-time' in study_mode_and_duration.get_text(strip=True)):
            continue

        programme_code_and_entry = block.find('div', class_='programmes-code-and-entry-description').get_text(strip=True).split('|')[0].strip()
        title = block.find('div', class_='title').get_text(strip=True)
        subtitle = block.find('div', class_='subtitle').get_text(strip=True)
        deadlines = block.find_all('div', class_='early-deadline')
        print(f"programme_code_and_entry: {programme_code_and_entry}, title: {title}, subtitle: {subtitle}")
        if len(deadlines) == 0:
            deadline = "empty"
        else:
            local_deadline = deadlines[0].get_text(strip=True).replace('Application Deadline:', '').strip()
            non_local_deadline = deadlines[1].get_text(strip=True).replace('Non Local Application Deadline:', '').strip()
            deadline = f"local: {local_deadline}, non-local: {non_local_deadline}"
        programmes_data.append([programme_code_and_entry, title + ' ' + subtitle, deadline])

    return pd.DataFrame(programmes_data, columns=['Code', 'Programme', 'Deadline'])


def parse_html_json(html):
    # 首先将unicode字符转换成普通字符串
    data = json.loads(html)
    # 按照json格式打印data，好看的格式
    # print(json.dumps(data, indent=4))
    html = data[-2]['data']
    html = unescape(html)

    # 定义正则表达式，提取专业名称和截止日期
    programme_pattern = re.compile(r'class="title">(.*?)<\/div>')
    deadline_pattern = re.compile(
        r'Application Deadline: <time datetime=".*?" class="time">(.*?)<\/time>')

    # 使用正则表达式查找所有匹配项
    programme_matches = programme_pattern.findall(html)
    deadline_matches = deadline_pattern.findall(html)

    # 检查匹配数量是否相同，如果不同则抛出异常
    if len(programme_matches) != len(deadline_matches):
        raise ValueError("Mismatch between programme names and deadlines.")

    # 创建数据存储列表
    programmes_data = []

    # 遍历匹配结果，提取信息
    for programme, deadline in zip(programme_matches, deadline_matches):
        # 提取专业代码和入学时间
        programme_code_and_entry = re.search(r'\d{5} \| (.*) Entry',
                                             programme).group(1)

        # 提取全称和学位
        title = re.search(r'([^-]*) -', programme).group(1).strip()
        subtitle = re.search(r' - (.*)$', programme).group(1).strip()

        # 将提取的信息添加到列表中
        programmes_data.append(
            [programme_code_and_entry, title + ' ' + subtitle, deadline])

    # 将列表转换为 DataFrame
    return pd.DataFrame(programmes_data,
                        columns=['Code', 'Programme', 'Deadline'])



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
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
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
