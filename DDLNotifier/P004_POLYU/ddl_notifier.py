import os
import json
from bs4 import BeautifulSoup
import requests
import pandas as pd
from DDLNotifier.utils.compare_and_notify import compare_and_notify
from DDLNotifier.config import CONFIG
from html import unescape
import re

# Constants
URL = 'https://www.polyu.edu.hk/study/pg/taught-postgraduate'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, 'programme_data.xlsx')  # Save path for the CSV
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")
recipient_email = CONFIG.RECIPEINT_EMAIL
school_name = BASE_PATH.split('_')[-1]

def download_html_old(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def download_html(url):
    # 构建请求的 URL，之前是ajax，现在已经改成直接请求网页
    # url = 'https://www.polyu.edu.hk/study/views/ajax?_wrapper_format=drupal_ajax'

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
    # 之前需要从ajax的json中提取html，现在直接从html中提取
    # data = json.loads(html)
    # # Assuming the HTML content is in the last 'data' element
    # html_content = unescape(data[-2]['data'])
    html_content = html

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
        if 'doctor' in title.lower() or 'doctor' in subtitle.lower():
            continue
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
    compare_and_notify(old_data, new_data, log_file, school_name)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_EXCEL, index=False)

if __name__ == "__main__":
    main()
