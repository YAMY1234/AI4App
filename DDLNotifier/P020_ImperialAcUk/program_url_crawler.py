import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://www.imperial.ac.uk/study/courses/?courseType=postgraduate+taught&courseStartDate=2025&page=100"):
    # 发送GET请求并获取网页内容
    response = requests.get(url, verify=False)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程名称和链接的HTML元素
    course_elements = soup.find_all("h4", class_="course-card__title")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for course in course_elements:
        link_element = course.find("a")
        if link_element:
            program_name = link_element.text.strip()
            program_link = urljoin(url, link_element['href'])

            # 将信息添加到DataFrame中
            data["ProgramName"].append(program_name)
            data["URL Link"].append(program_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel("programs.xlsx", index=False)


# 调用爬虫函数
if __name__ == '__main__':
    crawl()
