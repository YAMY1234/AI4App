import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import json
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def extract_json_from_html(html_text):
    start_marker = 'window.REDUX_DATA = '
    start_index = html_text.find(start_marker) + len(start_marker)

    if start_index == -1:
        raise ValueError("无法找到JSON起始位置")

    count = 0
    end_index = start_index

    for i in range(start_index, len(html_text)):
        if html_text[i] == '{':
            count += 1
        elif html_text[i] == '}':
            count -= 1
        if count == 0:
            end_index = i + 1
            break

    json_string = html_text[start_index:end_index]
    json_string = json_string.replace('undefined', 'true')
    print(json_string)

    try:
        json_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析失败: {e}")

    return json_data

def crawl():
    base_url = "https://www.birmingham.ac.uk/study/postgraduate/course-search"
    query_params = {
        "academicLevel": "e2ad4c71-7518-45d7-b1a2-c1280513496c",
        "courseStructure": "a6575da0-f868-4842-bbd8-288437f56505",
        "preventScrollTop": "true",
        "qualification": "9af0f287-d32f-4daf-8ce3-c75e14bac00b",
        "studyLevel": "Postgraduate taught",
        "studyPattern": "full time"
    }

    data = {"ProgramName": [], "URL Link": []}

    for page in range(1, 31):
        query_params['pageIndex'] = page
        page_url = f"{base_url}?{requests.utils.unquote(requests.compat.urlencode(query_params))}"
        response = requests.get(page_url, verify=False)

        # 示例使用方法
        response_text = response.text  # 这里假设response.text包含整个HTML响应内容
        json_data = extract_json_from_html(response_text)
        print(f"json_data: {json_data}")

        # 假设我们需要提取的信息在json_data中的某个嵌套结构中
        # 这里以courses为例，需根据实际JSON结构调整
        courses = json_data.get('search', {}).get('listings', {}).get('courses', {}).get('results', [])
        print(f"courses: {courses}")
        for course in courses:
            program_name = course.get('title', '')
            program_link = course.get('url', '')
            if program_name and program_link:
                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


# 调用爬虫函数
if __name__ == '__main__':
    crawl()
