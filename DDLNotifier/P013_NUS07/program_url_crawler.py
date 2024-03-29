import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://medicine.nus.edu.sg/graduatestudies/education/coursework-programmes/"):
    webScraper = WebScraper()  # 假设WebScraper是已经定义好的用于获取HTML的类
    response_text = webScraper.get_html(url)

    soup = BeautifulSoup(response_text, "html.parser")

    # 查找所有class="fl-callout-title-link fl-callout-title-text"的a标签
    a_tags = soup.find_all('a',
                           class_="fl-callout-title-link fl-callout-title-text")

    program_links = []
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
