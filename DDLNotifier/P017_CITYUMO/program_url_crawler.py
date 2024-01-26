import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 设置复杂的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1", # 不跟踪请求
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # 发送GET请求并获取网页内容
    url = "https://www.ln.edu.hk/sgs/taught-postgraduate-programmes/programme-on-offer"
    response = requests.get(url, headers=headers)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程信息的div元素
    course_elements = soup.find_all("div", class_="col-md-6 col-sm-6 mb-4")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for course_element in course_elements:
        # 提取课程名称
        program_name_element = course_element.find("h5")
        program_name = program_name_element.get_text().strip() if program_name_element else None

        # 提取课程的详细信息链接
        link_element = course_element.find("a", href=True)
        url_link = "https://www.ln.edu.hk" + link_element["href"] if link_element else None

        if program_name and url_link:
            # 将信息添加到DataFrame中
            data["ProgramName"].append(program_name)
            data["URL Link"].append(url_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
