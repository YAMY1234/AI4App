import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 发送GET请求并获取网页内容
    url = "https://gs.hkbu.edu.hk/programmes?type%5B%5D=taught-postgraduate-programmes"
    response = requests.get(url, verify=False)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程信息的HTML元素
    course_elements = soup.find_all("a", href=True)

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for course_element in course_elements:
        program_name = course_element.text.strip()
        if not ("/programmes/" in course_element["href"]):
            continue
        url_link = "https://gs.hkbu.edu.hk" + course_element["href"]

        # 将信息添加到DataFrame中
        data["ProgramName"].append(program_name)
        data["URL Link"].append(url_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)
