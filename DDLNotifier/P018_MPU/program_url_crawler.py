import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 发送GET请求并获取网页内容
    base_url = "https://www.mpu.edu.mo/"
    relative_path = "admission_mainland/zh/postgraduate_mainland.php"
    url = urljoin(base_url, relative_path)
    response = requests.get(url)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程信息的HTML元素
    course_elements = soup.find_all("table", class_="color-tbl2")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for table in course_elements:
        rows = table.find_all("tr")[1:]  # 忽略表头
        for row in rows:
            cols = row.find_all("td")
            if cols and len(cols) > 0:
                program_name = cols[0].text.strip()
                link_element = cols[0].find("a")
                if link_element and 'href' in link_element.attrs:
                    program_link = urljoin(base_url, link_element['href'])
                else:
                    program_link = "No link available"

                # 将信息添加到DataFrame中
                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


# 调用爬虫函数
crawl()
