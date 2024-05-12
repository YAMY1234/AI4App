from datetime import datetime

from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG  # Replace with your actual email module
from DDLNotifier.P024_KCL.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
SAVE_PATH_NEW_XLSX_WITH_TIMESTAMP = os.path.join(BASE_PATH, f"program_deadlines-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx")

log_file = os.path.join(BASE_PATH, "notification_log.txt")

'''
export OPENSSL_CONF=/etc/ssl/openssl.cnf
python /root/AI4App/DDLNotifier/notifier_routine.py
'''

options = Options()
options.add_argument("--headless")  # Runs Chrome in headless mode.

def get_deadline(url):
    """Fetches the application closing date guidance text from the specified URL."""
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,
                                          "div.Richtextstyled__RichtextStyled-sc-1kvg2vc-0 p.Paragraphstyled__ParagraphStyled-sc-176xsi4-0"))
    )
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        header = soup.find("h4", string=lambda text: text and "Application closing date guidance" in text)
        print(f"Debug: Header found - {header.text if header else 'No header found'}")  # Debug output

        if header:
            content = []
            # Start collecting all sibling elements until another header is found or no more siblings
            for sibling in header.find_next_siblings():
                content.append(" ".join(sibling.stripped_strings))
            text = " ".join(content)
            return text if text else "Application deadline information not found"
        else:
            return "Closing date section not found"
    except Exception as e:
        return f"Error retrieving information: {str(e)}"

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)

def main():
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
        compare_and_notify(old_data, new_data, log_file, school_name)

    # Save the new data for future comparisons
    new_data.to_excel(SAVE_PATH_NEW_XLSX, index=False)

    # 保存    programs-当前时间戳.xlsx
    new_data.to_excel(f"program_deadlines-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx", index=False)

    # 检查当前文件夹下时间戳后缀为3天之前的文件，如果存在则删除
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        print(file)
        if file.startswith("program_deadlines-") and file.endswith(".xlsx"):
            file_time = pd.Timestamp(file.split("-")[1].split(".")[0])
            if pd.Timestamp.now() - file_time >= pd.Timedelta(days=3):
                os.remove(file)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")


# Run the main function
if __name__ == "__main__":
    main()

