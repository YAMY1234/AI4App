from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from DDLNotifier.config import CONFIG  # 替换为你的邮件模块配置
from DDLNotifier.P003_HKUST.program_url_crawler import crawl
from DDLNotifier.utils.compare_and_notify import compare_and_notify  # 导入通用函数

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
school_name = BASE_PATH.split('_')[-1]
PROGRAM_DATA_EXCEL = os.path.join(BASE_PATH, 'programs.xlsx')
recipient_email = CONFIG.RECIPEINT_EMAIL

SAVE_PATH_OLD_XLSX = os.path.join(BASE_PATH, 'program_deadlines.xlsx')
SAVE_PATH_NEW_XLSX = os.path.join(BASE_PATH, 'program_deadlines.xlsx')
log_file = os.path.join(BASE_PATH, "notification_log.txt")  # 日志文件路径

def get_deadline(url):
    # 发送GET请求
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'  # 根据网页实际编码调整
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找Application Deadlines部分
    deadline_section = soup.find('div', class_='block-row-heading', text='Application Deadlines').find_next_sibling('div', class_='block-row-content')

    # 提取文字
    deadlines_text = deadline_section.get_text(separator="\n", strip=True)

    return deadlines_text

def get_current_programs_and_urls():
    return pd.read_excel(PROGRAM_DATA_EXCEL)

def main():
    # 先抓取最新的项目 URL
    crawl()
    current_program_data = get_current_programs_and_urls()

    new_data_list = []
    # 注意：这里构造的数据列名使用 "Programme" 和 "Deadline"，以与 compare_and_notify 中的逻辑匹配
    for index, row in current_program_data.iterrows():
        programme = row['ProgramName']  # 如果 Excel 中名称是 ProgramName，可以转换成 Programme
        url_link = row['URL Link']
        try:
            deadline = get_deadline(url_link)
            new_data_list.append({'Programme': programme, 'Deadline': deadline})
            print(f"Retrieved deadlines for {programme}, deadline: {deadline}")
        except Exception as e:
            print(f"Error retrieving deadlines for {programme}: {e}")

    new_data = pd.DataFrame(new_data_list)

    # 读取旧数据（如果存在）
    old_data = pd.DataFrame()
    if os.path.exists(SAVE_PATH_OLD_XLSX):
        old_data = pd.read_excel(SAVE_PATH_OLD_XLSX)

    # 使用通用的 compare_and_notify 函数进行比较和通知
    if not old_data.empty:
        compare_and_notify(old_data, new_data, log_file, school_name)
    else:
        print("No old data to compare with. Saving new data.")

    # 保存最新数据
    new_data.to_excel(SAVE_PATH_NEW_XLSX, index=False)
    print(f"Deadlines updated and saved to {SAVE_PATH_NEW_XLSX}")

if __name__ == "__main__":
    main()