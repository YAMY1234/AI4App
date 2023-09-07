import requests
from bs4 import BeautifulSoup
from config.program_details_header import header
import re

# 请求的URL
url = "https://www.ucl.ac.uk/prospective-students/graduate/system/ajax"

# 请求表单页面
url_form = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/health-wellbeing-and-sustainable-buildings-msc"
response = requests.get(url_form)

# 使用 BeautifulSoup 解析页面
soup = BeautifulSoup(response.text, 'html.parser')

# 提取 form_build_id
form_build_id = soup.find('input', {'name': 'form_build_id'})['value']


# 设置请求头信息
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.ucl.ac.uk",
    "Referer": "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/health-wellbeing-and-sustainable-buildings-msc",
    "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# 如果POST请求需要数据，您需要在下面的数据字典中添加
data = {
    'ucl_international_equivalencies': 'CN',
    'form_build_id': form_build_id,
    'form_id': 'ucl_programmes_international_equivalencies_form',
    '_triggering_element_name': 'ucl_international_equivalencies'
}

response = requests.post(url, headers=headers, data=data)

# print(response.text)
# print(response.status_code)

#
# # 解析返回的JSON数据
json_data = response.json()

print(json_data)


# 从响应中获取 JSON 数据
json_data = response.json()

all_text = ""

# 遍历 JSON 数据，查找 "command": "insert" 的项
for item in json_data:
    if item.get('command') == 'insert':
        # 使用 BeautifulSoup 提取 data 中的 <p> 标签内容
        soup = BeautifulSoup(item['data'], 'html.parser')
        p_tags = soup.find_all('p')
        for p in p_tags:
            all_text += p.text + ' '

# 使用正则表达式匹配文本中的百分比
match = re.search(r'(\d{2})%', all_text)

program_details = {}

if match:
    percentage = int(match.group(1))
    if percentage == 80:
        program_details[header.cn_requirement] = "2:2"
    elif percentage == 85:
        program_details[header.cn_requirement] = "2:1"
    else:
        program_details[header.cn_requirement] = "其他"
