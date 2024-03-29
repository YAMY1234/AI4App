import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://bschool.nus.edu.sg/"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers)
    response_text = response.text

    webScraper = WebScraper()

    if response.status_code != 200:
        print("网页获取失败，URL不正确！！")
    elif "ROBOT" in response_text or "robot" in response_text:
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
