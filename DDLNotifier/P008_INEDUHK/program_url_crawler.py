import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

from pandas.core.interchange.dataframe_protocol import DataFrame

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def parse_programs(soup) -> DataFrame:
    elements = soup.find_all("div", class_="box16 programe_row_1")
    for index, elem in enumerate(elements[:5]):
        print(f"Element {index + 1} HTML: {elem.prettify()}")
    data = {"ProgramName": [], "URL Link": []}
    for element in elements:
        program_name_tag = element.find("h5")
        link_element = element.find("a", href=True)
        if program_name_tag and link_element:
            program_name = program_name_tag.get_text().strip()
            url_link = "https://www.ln.edu.hk" + link_element["href"]
            # Print the program name and URL link for debugging
            print(f"Program Name: {program_name}, URL: {url_link}")
            # Add information to the DataFrame
            data["ProgramName"].append(program_name)
            data["URL Link"].append(url_link)
    return pd.DataFrame(data)


def parse_programs_2025(soup) -> DataFrame:
    data = {"ProgramName": [], "URL Link": [], "Deadline": []}
    tables = soup.find_all("table")
    if not tables:
        print("未找到表格")
        return pd.DataFrame(data)
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 6:
                # 获取项目名称，包含中文和英文
                program_name_td = cols[0]
                program_name = program_name_td.get_text(separator=' ', strip=True)
                # 获取链接
                url_td = cols[4]
                link_tag = url_td.find("a", href=True)
                if link_tag:
                    url_link = link_tag["href"]
                else:
                    url_link = ''
                # 获取deadline
                ddl_td = cols[3]
                ddl_text = ddl_td.get_text(strip=True)
                # 打印调试信息
                print(f"项目名称: {program_name}, 链接: {url_link}, deadline: {ddl_text}")
                # 添加数据到字典
                data["ProgramName"].append(program_name)
                data["URL Link"].append(url_link)
                data["Deadline"].append(ddl_text)
    return pd.DataFrame(data)


def crawl():
    # url = "https://www.ln.edu.hk/sgs/taught-postgraduate-programmes/programme-on-offer"
    url = "https://www.ln.edu.hk/sgs/programmes-on-offer-2025-26-intake"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    df = parse_programs_2025(soup)
    print(df)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)

if __name__ == "__main__":
    crawl()
