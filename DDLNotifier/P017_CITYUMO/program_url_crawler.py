import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://cityu.edu.mo/zh/%e8%aa%b2%e7%a8%8b/%e7%a2%a9%e5%a3%ab%e5%ad%b8%e4%bd%8d%e8%aa%b2%e7%a8%8b/"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到所有符合特定样式的<td>标签
        td_tags = soup.find_all('td', style=lambda value: value and "width: 300px;" in value)

        data = {"ProgramName": [], "URL Link": []}

        # 遍历所有的<td>标签
        for td in td_tags:
            # 提取<a>标签
            a_tag = td.find('a', href=True, style=lambda value: value and "border: 3px solid" in value)
            program_name = a_tag.get_text().strip() if a_tag else None
            if not program_name or "碩士" not in program_name:
                continue
            url_link = a_tag['href'] if a_tag else None

            if program_name and url_link:
                data["ProgramName"].append(program_name)
                data["URL Link"].append(url_link)
        if not data["ProgramName"]:
            print("未找到匹配的项目名称和链接")
    else:
        print("无法获取网页内容，HTTP状态码:", response.status_code)

    df = pd.DataFrame(data)
    df.to_excel("programs.xlsx", index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
