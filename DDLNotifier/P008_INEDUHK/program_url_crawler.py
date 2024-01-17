import requests
from bs4 import BeautifulSoup
import pandas as pd
import osPROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 发送GET请求并获取网页内容
    url = "https://www.ln.edu.hk/sgs/taught-postgraduate-programmes/programme-on-offer"
    response = requests.get(url)

    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到所有包含课程信息的div元素
    course_elements = soup.find_all("div", class_="content-last")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for course_element in course_elements:
        program_name = course_element.h5.get_text().strip() if course_element.h5 else None
        link_element = course_element.find_parent("a", href=True)
        if program_name and link_element:
            url_link = "https://www.ln.edu.hk" + link_element["href"]
            # 将信息添加到DataFrame中
            data["ProgramName"].append(program_name)
            data["URL Link"].append(url_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)

# 运行爬虫
crawl()
