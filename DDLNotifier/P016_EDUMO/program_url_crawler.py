import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://grs.um.edu.mo/index.php/prospective-students/master-postgraduate-certificate-diploma-programmes/"):
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

        # 修改lambda表达式，确保text不是None
        master_programmes_th = soup.find_all('th', string=lambda
            text: text and "Master’s Degree & Postgraduate Certificate/Diploma Programmes" in text)
        if master_programmes_th:
            last_master_programmes_th = master_programmes_th[-1]

            # 找到<th>标签后的所有<li>标签
            li_tags = last_master_programmes_th.find_all_next('li')

            data = {"ProgramName": [], "URL Link": []}

            # 遍历所有的<li>标签
            for li in li_tags:
                # 提取专业名称和链接
                a_tag = li.find('a', href=True)
                program_name = a_tag.get_text().strip() if a_tag else None
                url_link = a_tag['href'] if a_tag else None

                if program_name and url_link:
                    data["ProgramName"].append(program_name)
                    data["URL Link"].append(url_link)
        else:
            print("未找到匹配的<th>标签")
    else:
        print("无法获取网页内容，HTTP状态码:", response.status_code)

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
