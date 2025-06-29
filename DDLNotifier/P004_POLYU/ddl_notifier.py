import os
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



def download_html(url, year_value="2634"):
    """直接 GET 完整页面，避免 AJAX 的不稳定字段"""
    params = {
        "pg_programmes_semester_term_value": year_value,
        "pg_programmes_faculty_school_target_id_verf": "All",
        "combine": ""
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    # 使用 GET 请求获取完整页面
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    
    print(f"成功获取页面，学期参数: {year_value}")
    return response.text


def parse_html(html: str) -> pd.DataFrame:
    """解析 HTML 内容，提取课程信息"""
    soup = BeautifulSoup(html, "html.parser")
    programmes_data = []
    
    # 使用 CSS 选择器查找所有课程区块
    for block in soup.select("div.views-row"):
        # 1) 检查学习模式 - Full-time / Mixed-Mode 兼容
        study_elem = block.select_one(".study-mode-and-duration")
        if not study_elem or "Full-time" not in study_elem.get_text():
            continue
        
        # 2) 获取课程代码
        code_elem = block.select_one(".programmes-code-and-entry-description")
        if not code_elem:
            continue
        programme_code = code_elem.get_text(strip=True).split("|")[0].strip()
        
        # 3) 获取标题和副标题
        title_elem = block.select_one(".title")
        title = title_elem.get_text(strip=True) if title_elem else ""
        subtitle_elem = block.select_one(".subtitle")
        subtitle = subtitle_elem.get_text(strip=True) if subtitle_elem else ""
        
        # 如果标题或副标题中含有 "doctor" 则跳过（不处理博士级别课程）
        if 'doctor' in title.lower() or 'doctor' in subtitle.lower():
            continue
        
        # 4) 提取 deadline 信息 - 允许只有一行或包含 Closed 的情况
        deadline_elements = block.select(".deadline-section .early-deadline")
        if not deadline_elements:
            # 兼容旧的结构
            deadline_elements = block.select(".early-deadline")
        
        deadlines = []
        for elem in deadline_elements:
            deadline_text = elem.get_text(strip=True)
            # 清理文本
            deadline_text = deadline_text.replace('Application Deadline:', '').replace('Non Local Application Deadline:', '').strip()
            if deadline_text:
                deadlines.append(deadline_text)
        
        deadline_str = " | ".join(deadlines) if deadlines else "empty"
        
        # 5) 构建完整课程名称
        programme_name = f"{title} {subtitle}".strip()
        full_programme_name = f"{programme_code} - {programme_name}"
        
        # 调试输出
        print(f"Code: {programme_code}, Programme: {full_programme_name}, Deadline: {deadline_str}")
        
        programmes_data.append([programme_code, full_programme_name, deadline_str])
    
    return pd.DataFrame(programmes_data, columns=["Code", "Programme", "Deadline"])


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
