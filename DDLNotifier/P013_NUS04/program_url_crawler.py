import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://scale.nus.edu.sg/programmes/graduate"):
    webScraper = WebScraper()  # 假设WebScraper是已经定义好的用于获取HTML的类
    response_text = webScraper.get_html(url)

    soup = BeautifulSoup(response_text, "html.parser")
    # 查找所有包含项目信息的<div>标签
    div_tags = soup.find_all('div', class_='dropdown-menu-section col-md-3')

    program_links = []
    for div_tag in div_tags:
        # 检查第一个<a>标签是否包含"Graduate"
        first_a_tag = div_tag.find('a')
        if first_a_tag and "Graduate" in first_a_tag.text:
            # 获取除了"Graduate"外的所有<a>标签
            a_tags = div_tag.find_all('a')[1:]  # 跳过第一个，因为它是"Graduate"
            for a_tag in a_tags:
                program_name = a_tag.text.strip()
                program_link = a_tag['href']
                program_links.append({
                    "ProgramName": program_name,
                    "URL Link": program_link
                })

    # 将链接列表转换为pandas DataFrame
    program_links_df = pd.DataFrame(program_links)

    # 将DataFrame保存到Excel文件，不包括索引
    program_links_df.to_excel("programs.xlsx", index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
