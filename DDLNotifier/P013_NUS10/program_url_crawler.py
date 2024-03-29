import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://lkyspp.nus.edu.sg/"):
    webScraper = WebScraper()  # 假设WebScraper是已经定义好的用于获取HTML的类
    response_text = webScraper.get_html(url)

    soup = BeautifulSoup(response_text, "html.parser")

    # 查找带有"/graduate-programmes"链接的<a>标签，然后找到其紧随的<ul>标签
    graduate_programmes_a_tag = soup.find_all('a', href="/graduate-programmes", title="Programmes", text="Programmes")
    graduate_programmes_a_tag = graduate_programmes_a_tag[-1]
    if graduate_programmes_a_tag:
        parent_tag = graduate_programmes_a_tag.parent

        # 从<a>标签的父节点找到紧随其后的<ul>标签
        ul_tag = parent_tag.find_next('ul')
        program_links = []
        # 在<ul>标签中找到所有<li>标签
        li_tags = ul_tag.find_all('li')
        for li_tag in li_tags:
            a_tag = li_tag.find('a')
            if a_tag:
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
    else:
        print("No graduate programmes found.")


# 运行爬虫
if __name__ == "__main__":
    crawl()
