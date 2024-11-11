import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/taught&edition=2024"):
    # 发送GET请求并获取网页内容
    timeout_duration = 5
    cnt = 30
    while cnt > 0:
        try:
            response = requests.get(url, verify=False, timeout=timeout_duration)
            break
        except requests.Timeout:
            cnt += 1
            print(f"Timeout. Increasing timeout duration to {timeout_duration} seconds...")
            continue
    if cnt == 0:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
            log_file.write(f"ERROR !! cnt == 10 \n")
        return
    print(response.text)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程名称和链接的HTML元素
    # 根据新的HTML结构进行调整
    course_elements = soup.find_all("a", class_="list-group-item")
    if len(course_elements) == 0:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt"), "a") as log_file:
            log_file.write(f"ERROR !! len(course_elements) == 0 \n")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for course in course_elements:
        # 检查是否包含特定的<span>标签
        if course.find("span", class_="label label-primary pull-right"):
            continue  # 如果存在这个标签，跳过当前项

        # 提取课程名称和链接
        program_name = course.text.strip()  # https://postgraduate.degrees.ed.ac.uk/index.php
        # program_link = urljoin(url, course['href'])
        program_link = "https://postgraduate.degrees.ed.ac.uk" + course['href']
        # 将信息添加到DataFrame中
        data["ProgramName"].append(program_name)
        data["URL Link"].append(program_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)



# 调用爬虫函数
if __name__ == '__main__':
    crawl()
