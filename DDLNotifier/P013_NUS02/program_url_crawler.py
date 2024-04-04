import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://bschool.nus.edu.sg/"):
    webScraper = WebScraper()

    response_text = webScraper.get_html(url)

    soup = BeautifulSoup(response_text, "html.parser")

    # 找到页面上的所有<div class="col-lg-6">
    col_lg_6_divs = soup.find_all('div', class_='tab-content home-column-main-tab-content-child-content')

    # 选择第二个和第三个<div class="col-lg-6">
    target_divs = col_lg_6_divs[1:3]  # Python切片是左闭右开区间

    data = {"ProgramName": [], "URL Link": []}

    for div in target_divs:
        # 在每个目标<div>中查找<img>和<a>标签
        img_tags = div.find_all('img', alt=True,  class_="lazyload img-fluid")
        a_tags = div.find_all('a', href=True)
        for img_tag, a_tag in zip(img_tags, a_tags):
            program_name = img_tag['alt'].strip()
            url_link = a_tag['href'].strip()
            data["ProgramName"].append(program_name)
            data["URL Link"].append(url_link)
    df = pd.DataFrame(data)
    df.to_excel("programs.xlsx", index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
