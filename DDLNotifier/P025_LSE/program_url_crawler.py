import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(base_url="https://www.lse.ac.uk/study-at-lse/Graduate/Available-programmes"):
    data = {"ProgramName": [], "URL Link": [], "Overseas": []}

    print(f"Fetching data from: {base_url}")
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {base_url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 根据示例结构，先锁定含有专业信息的 accordion 区域
    accordion_sections = soup.find_all('section', class_='accordion')
    if not accordion_sections:
        print("No accordion sections found.")
        return

    # 遍历每个 <section> 内的表格
    for section in accordion_sections:
        tables = section.find_all('table')
        for table in tables:
            tbody = table.find('tbody')
            if not tbody:
                continue

            rows = tbody.find_all('tr')
            # 跳过表头行
            for row in rows[1:]:
                # 查找包含专业名称的 <a> 标签
                program_link_tag = row.find('a', class_='sys_16')
                if not program_link_tag:
                    continue

                program_name = program_link_tag.get_text(strip=True)
                href = program_link_tag.get('href', '')

                # 提取当前行的所有 <td> 标签，注意第一个 <td> 已包含专业名称
                tds = row.find_all('td')
                # 根据结构，第二个<td>为 Home，第三个<td>为 Overseas，需提取第三个<td>
                if len(tds) >= 3:
                    overseas_value = tds[2].get_text(strip=True)
                else:
                    overseas_value = ""

                data["ProgramName"].append(program_name)
                data["URL Link"].append(href)
                data["Overseas"].append(overseas_value)

                print(f"Added program: {program_name}, URL: {href}, Overseas: {overseas_value}")

    if not data["ProgramName"]:
        print("No programs were added to the list.")
        return

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)
    print(f"Data successfully saved to Excel: {PROGRAM_DATA_EXCEL}")


if __name__ == '__main__':
    crawl()

