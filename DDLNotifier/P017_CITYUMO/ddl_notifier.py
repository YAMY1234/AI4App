from datetime import datetime
import requests
from PyPDF2 import PdfReader
import io
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P017_CITYUMO.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify

# Constants
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

school_name = BASE_PATH.split('_')[-1]
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')  # CSV file with current program data

recipient_email = CONFIG.RECIPEINT_EMAIL  # Replace with your actual email for notifications
# recipient_email = 'yamy12344@gmail.com'  # Replace with your actual email for notifications
SAVE_PATH_OLD_XLSX = 'program_deadlines.xlsx'  # Save path for the old Excel file
SAVE_PATH_NEW_XLSX = 'program_deadlines.xlsx'  # Save path for the new Excel file
SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, SAVE_PATH_OLD_XLSX)  # Save path for the HTML
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, SAVE_PATH_NEW_XLSX)  # Save path for the CSV

log_file = os.path.join(BASE_PATH, "notification_log.txt")

constant_deadline = None

def get_constant_deadline():
    def download_pdf(url):
        response = requests.get(url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            raise Exception("无法下载PDF文件。")

    def extract_text_from_pdf(pdf_file):
        reader = PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

    def search_pattern_in_text(text, pattern):
        matches = re.findall(pattern, text, re.MULTILINE)
        return matches

    # PDF URL
    pdf_url = "https://ado.cityu.edu.mo/uploads/userfiles/2024%E5%B9%B4%E5%86%85%E5%9C%B0%E6%8B%9B%E7%94%9F%E7%AE%80%E7%AB%A0.pdf"

    try:
        # 下载PDF文件
        pdf_file = download_pdf(pdf_url)

        # 提取文本
        pdf_text = extract_text_from_pdf(pdf_file)

        # 搜索特定模式的文本（"硕士/" 后的一行文字）
        pattern = r'硕士/([^\n]+)'
        result = search_pattern_in_text(pdf_text, pattern)

        # 输出匹配结果
        print(result)
        return result[0]

    except Exception as e:
        print(e)
        return "日期未找到"

def get_deadline(url=None):
    return constant_deadline


def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)


def main():
    global constant_deadline
    constant_deadline = get_constant_deadline()
    crawl()
    # Read current program data
    current_program_data = get_current_programs_and_urls()

    # Prepare a list to collect new data
    new_data_list = []

    # Get the new deadline data
    for index, row in current_program_data.iterrows():
        program_name = row['ProgramName']
        url_link = row['URL Link']
        try:
            deadline_text = get_deadline(url_link)
            new_data_list.append({'Programme': program_name, 'Deadline': deadline_text})
            print(f"Retrieved deadlines for {program_name}, deadline_text: {deadline_text}")
        except Exception as e:
            print(f"Error retrieving deadlines for {program_name}: {e}")

    # Create a new DataFrame from the list of new data
    new_data = pd.DataFrame(new_data_list)

    # Read old data if it exists
    old_data = pd.DataFrame()
    if os.path.exists(SAVE_PATH_OLD_XLSX):
        old_data = pd.read_excel(SAVE_PATH_OLD_XLSX)

    # If old data is not empty, compare and notify
    if not old_data.empty:
        compare_and_notify(old_data, new_data)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_NEW_XLSX, index=False)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()
