from datetime import datetime

import requests
from bs4 import BeautifulSoup
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
import pandas as pd
import os

from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
URL = 'https://gs.hsu.edu.hk/en/programme-information/'
# URL = 'https://admission.hsu.edu.hk/taught-postgraduate-admissions/programme-information/'
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

    # 1) 找到目标表格：优先按 id；若失败，则兜底按特征类名与表头关键字匹配
    table = soup.find('table', id='tablepress-47')
    if table is None:
        # 兜底策略：按类名 & 表头关键字定位
        candidates = soup.find_all('table', class_='tablepress')
        for t in candidates:
            thead = t.find('thead')
            if not thead:
                continue
            head_text = thead.get_text(separator=' ', strip=True).lower()
            if 'application deadlines' in head_text and 'non-local applicants' in head_text:
                table = t
                break
    if table is None:
        # 没找到表格就返回空 DataFrame，避免崩溃
        return pd.DataFrame(columns=['Programme', 'Deadline'])

    tbody = table.find('tbody') or table
    rows = tbody.find_all('tr')

    programmes_data = []

    for row in rows:
        tds = row.find_all('td')
        if not tds:
            continue

        # 跳过分组行（一般是 colspan=6 的学院标题行）
        first_td = tds[0]
        try:
            colspan = int(first_td.get('colspan', '1'))
        except ValueError:
            colspan = 1
        if colspan >= 6:
            continue

        # 2) 项目名称（优先 a 标签文本，否则用单元格纯文本）
        name_cell = first_td
        name_a = name_cell.find('a')
        programme_name = (name_a.get_text(strip=True) if name_a
                          else name_cell.get_text(separator=' ', strip=True))
        if not programme_name:
            continue

        # 去重保护（部分页面可能重复出现同名行）
        if any(p[0] == programme_name for p in programmes_data):
            continue

        # 3) Non-local Applicants 两列：
        #    根据页面结构：column-4 = Sep 2025 (Non-local)，column-5 = Jan 2026 (Non-local)
        #    为更稳妥，先尝试按类名取；若失败再回退到序号索引
        def clean_text(x):
            return x.get_text(separator=' ', strip=True) if x else ''

        # 尝试按类名
        nonlocal_sep = row.find('td', class_='column-4')
        nonlocal_jan = row.find('td', class_='column-5')
        sep_text = clean_text(nonlocal_sep)
        jan_text = clean_text(nonlocal_jan)

        # 若按类名没拿到，再按列序（通常表头是：Prog | L-Sep | L-Jan | NL-Sep | NL-Jan | Link）
        if not sep_text or not jan_text:
            # 确保索引安全
            # 期望至少 6 列；非严格页面也尽量容错
            if len(tds) >= 5:
                # 经验映射：td[3] = NL-Sep，td[4] = NL-Jan（0-based）
                sep_text = sep_text or clean_text(tds[3])
                jan_text = jan_text or clean_text(tds[4])

        # 规范化（将换行/括注合并为单行）
        sep_text = sep_text.replace('\n', ' ').strip()
        jan_text = jan_text.replace('\n', ' ').strip()

        # 4) 保持你原有 compare_and_notify 的列名：合并成单一 Deadline 字段
        deadline_combined = f"Non-local (Sep 2025): {sep_text} | Non-local (Jan 2026): {jan_text}"
        programmes_data.append([programme_name, deadline_combined])

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
