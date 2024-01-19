import requests
import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def get_with_pycurl(url):
    buffer = BytesIO()  # 创建一个缓冲区以存储响应内容

    c = pycurl.Curl()  # 创建一个 Curl 对象
    c.setopt(c.URL, url)  # 设置请求的 URL
    c.setopt(c.WRITEDATA, buffer)  # 将响应数据写入缓冲区
    # 可选：忽略 SSL 证书验证（如果需要的话）
    c.setopt(c.SSL_VERIFYPEER, 0)
    c.setopt(c.SSL_VERIFYHOST, 0)

    try:
        c.perform()  # 执行请求
    except pycurl.error as e:
        print('Error:', e)
    finally:
        c.close()  # 关闭 Curl 对象

    body = buffer.getvalue().decode('utf-8')  # 将响应内容转换为字符串
    return body



def crawl():
    # 发送GET请求并获取网页内容
    base_url = "https://www.mpu.edu.mo/"
    # relative_path = "admission_mainland/zh/postgraduate_mainland.php"
    # url = urljoin(base_url, relative_path)
    url = "https://www.mpu.edu.mo/admission_mainland/zh/postgraduate_mainland.php"
    # response = requests.get(url)
    response_t = get_with_pycurl(url)


    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response_t, "html.parser")

    # 找到所有包含课程信息的HTML元素
    course_elements = soup.find_all("table", class_="color-tbl2")

    # 创建一个空的DataFrame来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历每个课程元素并提取信息
    for table in course_elements:
        rows = table.find_all("tr")[1:]  # 忽略表头
        for row in rows:
            cols = row.find_all("td")
            if cols and len(cols) > 0:
                program_name = cols[0].text.strip()
                link_element = cols[0].find("a")
                if link_element and 'href' in link_element.attrs:
                    program_link = urljoin(base_url, link_element['href'])
                else:
                    program_link = "No link available"

                # 将信息添加到DataFrame中
                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 将数据保存到Excel文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


# 调用爬虫函数
if __name__ == '__main__':
    crawl()
