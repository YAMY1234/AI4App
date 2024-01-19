import requests
from bs4 import BeautifulSoup

def fetch_master_degree_date(url="https://www.mpu.edu.mo/admission_mainland/zh/pg_admissionroutes.php"):
    # 发送GET请求并获取网页内容
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找包含“硕士学位课程”文本的<strong>标签
    master_degree_heading = soup.find('strong', text='硕士学位课程')

    # 如果找到了这个标签，继续查找下一个<table>标签
    if master_degree_heading:
        table = master_degree_heading.find_next('table', class_='color-tbl3')
        if table:
            # 在表格中查找包含日期的<td>标签
            date_cell = table.find('td', class_='date')
            if date_cell:
                return date_cell.text.strip()

    return "日期未找到"

# 示例使用
url = "https://www.mpu.edu.mo/admission_mainland/zh/pg_admissionroutes.php"
date = fetch_master_degree_date(url)
print(date)
