import requests
from bs4 import BeautifulSoup

url = 'https://prog-crs.hkust.edu.hk/pgprog/2024-25/mpm'  # 在这里填入你的目标URL

def get_deadline(url):
    # 发送GET请求
    response = requests.get(url)
    response.encoding = 'utf-8'  # 根据网页实际编码调整

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找Application Deadlines部分
    deadline_section = soup.find('div', class_='block-row-heading', text='Application Deadlines').find_next_sibling('div', class_='block-row-content')

    # 提取文字
    deadlines_text = deadline_section.get_text(separator="\n", strip=True)

    print(deadlines_text)
    return deadlines_text