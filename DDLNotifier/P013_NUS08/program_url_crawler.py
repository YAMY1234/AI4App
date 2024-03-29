import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://www.ystmusic.nus.edu.sg/#"):
    webScraper = WebScraper()  # 假设WebScraper是已经定义好的用于获取HTML的类
    response_text = webScraper.get_html(url)
    soup = BeautifulSoup(response_text, "html.parser")

    # 查找包含“PROGRAMMES”文本的<li>标签，然后找到下一个<ul>
    programmes_li = soup.find_all(
        lambda tag: tag.name == 'li' and 'PROGRAMMES' in tag.text)[2]
    if not programmes_li:
        return "PROGRAMMES section not found."

    programmes_ul = programmes_li.find('ul')
    if not programmes_ul:
        return "No programmes listed under PROGRAMMES."

    program_links = []
    for li in programmes_ul.find_all('li', recursive=False):  # 只获取一级子标签<li>
        a_tag = li.find('a')
        if a_tag:
            program_name = a_tag.text.strip()
            program_link = a_tag.get('href',
                                     'default link')  # 如果没有href属性，则使用'default link'
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
