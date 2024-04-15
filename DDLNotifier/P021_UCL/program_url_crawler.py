import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees"):
    # 发送GET请求并获取网页内容
    response = requests.get(url, verify=False)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程名称和链接的HTML元素
    course_elements = soup.find_all("div", class_="result-item clearfix")

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

    # 保存    programs-当前时间戳.xlsx
    df.to_excel(f"programs-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx", index=False)

    # 检查当前文件夹下时间戳后缀为3天之前的文件，如果存在则删除
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        print(file)
        if file.startswith("programs-") and file.endswith(".xlsx"):
            file_time = pd.Timestamp(file.split("-")[1].split(".")[0])
            if pd.Timestamp.now() - file_time >= pd.Timedelta(days=3):
                os.remove(file)

# 调用爬虫函数
if __name__ == '__main__':
    crawl()
