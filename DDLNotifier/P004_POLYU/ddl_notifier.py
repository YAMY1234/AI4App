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
#
# def download_html(url):
#     # 构建请求的 URL，之前是ajax，现在已经改成直接请求网页
#     # url = 'https://www.polyu.edu.hk/study/views/ajax?_wrapper_format=drupal_ajax'
#
#     # 设置请求头（Headers）
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'X-Requested-With': 'XMLHttpRequest',
#         # ... 添加任何其他必要的头部信息
#     }
#
#     # 设置请求的正文数据（Payload）
#     payload = {
#         'pg_programmes_semester_term_value': '2516',
#         'pg_programmes_faculty_school_target_id_verf': 'All',
#         'combine': '',
#         'view_name': 'pg_programmes',
#         'view_display_id': 'programme_listing',
#         'view_args': '',
#         'view_path': '/node/91',
#         'view_base_path': '',
#         'view_dom_id': 'f2ccfb6a4d5d4058990775a2b0b169ed3d899a8e817cca54d022dffade6be84c',
#         'pager_element': '0',
#         '_drupal_ajax': '1',
#         'ajax_page_state[theme]': 'polyu_theme',
#         'ajax_page_state[theme_token]': '',
#         # ... 添加任何其他必要的正文信息
#     }
#
#     # 发送 POST 请求
#     response = requests.post(url, headers=headers, data=payload)
#
#     # 检查响应状态码
#     if response.status_code == 200:
#         # 打印响应的内容
#         print(response.text)
#     else:
#         print('Failed to retrieve data:', response.status_code)
#     return response.text



def download_html(url):
    # 请求 URL
    url = "https://www.polyu.edu.hk/study/views/ajax?_wrapper_format=drupal_ajax"

    # 请求头（部分请求头可根据实际情况调整）
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # 表单数据
    payload = {
        "pg_programmes_semester_term_value": "2609",
        "pg_programmes_faculty_school_target_id_verf": "All",
        "combine": "",
        "view_name": "pg_programmes",
        "view_display_id": "programme_listing",
        "view_args": "",
        "view_path": "/node/91",
        "view_base_path": "",
        "view_dom_id": "a2ab1a29db24f5f2a077fe57e8ca6636d7bd0a15c8f4d7fd465ee54c7caa0b41",
        "pager_element": "0",
        "_drupal_ajax": "1",
        "ajax_page_state[theme]": "polyu_theme",
        "ajax_page_state[theme_token]": "",
        "ajax_page_state[libraries]": (
            "better_exposed_filters/general,chosen/drupal.chosen,chosen_lib/chosen.css,extlink/drupal.extlink,"
            "google_tag/gtag,google_tag/gtag.ajax,lazy/lazy,paragraphs/drupal.paragraphs.unpublished,"
            "polyu_programme_page/translate,polyu_theme/block--config-pages--footer-configuration,"
            "polyu_theme/block--config-pages--header-configuration,polyu_theme/block--polyu-quick-access,"
            "polyu_theme/block--polyu-search-block--top,polyu_theme/block--polyu-theme-content,"
            "polyu_theme/paragraph--basic-info-block,polyu_theme/paragraph--dates-with-text,"
            "polyu_theme/paragraph--faq-standard-links,polyu_theme/paragraph--jupas-overview-block,"
            "polyu_theme/paragraph--key-dates,polyu_theme/paragraph--overview-expand-block,"
            "polyu_theme/paragraph--standard-banner,polyu_theme/paragraph--sub-footer-highlight-links,"
            "polyu_theme/pattern-uni-text,polyu_theme/styling,select2_all/drupal.select2,system/base,"
            "uni/fontawesome,uni/html,uni/really,uni/swiper,uni_theme/uni-card,uni_theme/uni-modal,"
            "views/views.module,views_infinite_scroll/views-infinite-scroll"
        )
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)

    # 遍历查找包含 HTML 的部分
    html_part = None
    for item in data:
        # 判断 item 中是否有 data 字段，并且数据不为空
        if item.get("data") and item.get("data").strip().startswith("<"):
            html_part = item["data"]
            break

    if html_part:
        print("提取到的 HTML 部分：")
        print(html_part)
    else:
        print("未找到 HTML 部分。")
    return html_part


def parse_html(html):
    # 直接使用传入的 HTML 内容
    html_content = html

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有 programme 区块，通常每个区块为一个 div.views-row
    programme_blocks = soup.find_all('div', class_='views-row')
    programmes_data = []

    for block in programme_blocks:
        # 获取学习模式与时长信息，如果没有则跳过
        study_mode_elem = block.find('div', class_='study-mode-and-duration')
        if not study_mode_elem:
            continue

        study_mode_text = study_mode_elem.get_text(strip=True)
        # 如果不包含 "Full-time" 则跳过
        if "Full-time" not in study_mode_text:
            continue

        # 获取 programme code 部分，并取 '|' 前面的部分
        code_elem = block.find('div', class_='programmes-code-and-entry-description')
        if not code_elem:
            continue
        programme_code = code_elem.get_text(strip=True).split('|')[0].strip()

        # 获取标题和副标题，如果不存在则设为空字符串
        title_elem = block.find('div', class_='title')
        title = title_elem.get_text(strip=True) if title_elem else ""
        subtitle_elem = block.find('div', class_='subtitle')
        subtitle = subtitle_elem.get_text(strip=True) if subtitle_elem else ""

        # 如果标题或副标题中含有 "doctor" 则跳过（不处理博士级别课程）
        if 'doctor' in title.lower() or 'doctor' in subtitle.lower():
            continue

        # 提取 deadline 部分，这里假定第一个 early-deadline 为本地申请截止，第二个为非本地申请截止
        deadlines_divs = block.find_all('div', class_='early-deadline')
        if len(deadlines_divs) >= 2:
            # 尝试获取 time 标签中的文本
            local_time = deadlines_divs[0].find('time')
            local_deadline = local_time.get_text(strip=True) if local_time else deadlines_divs[0].get_text(strip=True).replace('Application Deadline:', '').strip()
            non_local_time = deadlines_divs[1].find('time')
            non_local_deadline = non_local_time.get_text(strip=True) if non_local_time else deadlines_divs[1].get_text(strip=True).replace('Non Local Application Deadline:', '').strip()
            deadline = f"local: {local_deadline}, non-local: {non_local_deadline}"
        else:
            deadline = "empty"

        # 将标题和副标题合并作为完整的课程名称
        programme_name = f"{title} {subtitle}".strip()
        programme_name = f"{programme_code} - {programme_name}"

        # 调试输出
        print(f"Code: {programme_code}, Programme: {programme_name}, Deadline: {deadline}")

        programmes_data.append([programme_code, programme_name, deadline])

    return pd.DataFrame(programmes_data, columns=['Code', 'Programme', 'Deadline'])


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
