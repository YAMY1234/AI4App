import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl():
    base_url = "https://www.gla.ac.uk/postgraduate/taught/"
    response = requests.get(base_url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {"ProgramName": [], "URL Link": []}

    # 使用选择器捕获所有相关的li元素
    course_elements = soup.select("#jquerylist.programme-list > li")

    for course in course_elements:
        link_element = course.find("a")
        if link_element and 'href' in link_element.attrs:
            program_name = link_element.text.strip()
            program_link = urljoin(base_url, link_element['href'])
            data["ProgramName"].append(program_name)
            data["URL Link"].append(program_link)

    df = pd.DataFrame(data)
    df.to_excel('programs.xlsx', index=False)


# 调用爬虫函数
if __name__ == '__main__':
    crawl()
