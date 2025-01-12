import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(base_url="https://www.lse.ac.uk/study-at-lse/Graduate/Available-programmes"):
    data = {"ProgramName": [], "URL Link": []}

    print(f"Fetching data from: {base_url}")
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {base_url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有含有专业信息的表格，这里根据示例结构可先锁定 <section class="accordion"> 或直接找表格
    accordion_sections = soup.find_all('section', class_='accordion')
    if not accordion_sections:
        print("No accordion sections found.")
        return

    # 逐个 <section> 里查找 <table> 并逐行解析
    for section in accordion_sections:
        tables = section.find_all('table')
        for table in tables:
            tbody = table.find('tbody')
            if not tbody:
                continue

            rows = tbody.find_all('tr')
            # 跳过表头行（也可能直接从第二行开始）
            for row in rows[1:]:
                # 在 <td role="rowheader"> 或相应单元格中查找含有 class="sys_16" 的 <a> 标签
                program_link_tag = row.find('a', class_='sys_16')
                if not program_link_tag:
                    continue

                program_name = program_link_tag.get_text(strip=True)
                href = program_link_tag.get('href', '')

                # 如果链接是完整的 https，则直接用；否则可拼接主域名
                # 这里直接示例为完整链接
                data["ProgramName"].append(program_name)
                data["URL Link"].append(href)

                print(f"Added program: {program_name}, URL: {href}")

    if not data["ProgramName"]:
        print("No programs were added to the list.")
        return

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)
    print(f"Data successfully saved to Excel: {PROGRAM_DATA_EXCEL}")


if __name__ == '__main__':
    crawl()

