import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


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
        soup = BeautifulSoup(response.text, "html.parser")

        course_elements = soup.select(
            "ul.accommodationRoomListingstyled__BottomBorder-sc-dv1njo-1.hDkUYR > li")
        print(len(course_elements))

        for course in course_elements:
            link_element = course.find("a")
            if link_element and 'href' in link_element.attrs:
                program_name = course.select_one(
                    "div.Styles__TitleInner-fJiUNr.bPMpzi").text.strip()
                program_link = urljoin(page_url, link_element['href'])
                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

    df = pd.DataFrame(data)
    df.to_excel('programs.xlsx', index=False)

# 调用爬虫函数
if __name__ == '__main__':
    crawl()
