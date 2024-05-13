import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl():
    base_url = "https://courses.leeds.ac.uk/courses/course-search/masters-courses"
    data = {"ProgramName": [], "URL Link": []}

    # 循环页面从1到10
    for page in range(1, 21):
        query_params = {
            'type': 'PGT',
            'page': page,
            'complete_url': '?f.Delivery type|deliveryType=1&gscope1=MASTERS&f.Course type|searchCourseTypes=degree&num_ranks=15&query=!FunDoesNotExist:PadreNull&f.Academic year|term=202425&sort=title&collection=coursesv2&f.Mode of study|attendance=FT',
            'start_rank': 1 + (page - 1) * 15
        }
        page_url = f"{base_url}?{requests.utils.unquote(requests.compat.urlencode(query_params, safe='/:'))}"
        response = requests.get(page_url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")

        # 使用新的选择器寻找课程元素
        course_elements = soup.select("h2.uol-results-items__item__title")

        for course in course_elements:
            link_element = course.find("a")
            if link_element and 'href' in link_element.attrs:
                program_name = link_element.text.strip()
                program_link = urljoin(page_url, link_element['href'])
                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

    df = pd.DataFrame(data)
    df.to_excel('programs.xlsx', index=False)

# 调用爬虫函数
if __name__ == '__main__':
    crawl()
