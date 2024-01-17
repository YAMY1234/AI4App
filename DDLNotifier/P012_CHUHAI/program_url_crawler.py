import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 发送GET请求并获取网页内容
    url = "https://www.chuhai.edu.hk/en/Master%20of%20Architecture"
    response = requests.get(url)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 使用正则表达式匹配以“Master of”开头的项目名称
    program_pattern = re.compile(r'"Master of[^"]*"')

    # 找到所有匹配的项目名称
    program_matches = program_pattern.findall(str(soup))

    # 将匹配的结果转换为一个集合，然后转换为列表去除重复项
    program_names = list(set(program_matches))

    # 创建一个空的DataFrame来存储项目信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个项目名称并构建URL链接
    base_url = "https://www.chuhai.edu.hk/en/"
    for name in program_names:
        clean_name = name.strip('"')
        url_link = base_url + clean_name.replace(" ", "%20")

        # 将信息添加到DataFrame中
        data["ProgramName"].append(clean_name)
        data["URL Link"].append(url_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)

# 调用爬虫函数
if __name__ == "__main__":
    crawl()
