
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


def crawl(url="https://www.bristol.ac.uk/study/postgraduate/search/?q=&length=15&sort=score&dir=desc&sort=PostgraduateCourse-programtype&dir=asc&sort=PostgraduateCourse-programname&dir=asc&filterStudyType=Taught"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Use the correct class to find course elements
    course_elements = soup.find_all("article", class_="search-result--course")
    print(f"Found {len(course_elements)} course elements")

    data = {'ProgramName': [], 'URL Link': []}

    for course in course_elements:
        link_element = course.find("a", href=True)
        if link_element and course.find("h1"):
            program_name = course.find("h1").text.strip()
            program_link = link_element['href']
            full_url = f"https://www.bristol.ac.uk{program_link}"

            data['ProgramName'].append(program_name)
            data['URL Link'].append(full_url)
            print(f"Added: {program_name} - {full_url}")

    if data['ProgramName']:
        PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
        df = pd.DataFrame(data)
        df.to_excel(PROGRAM_DATA_EXCEL, index=False)
        print("Data successfully saved to Excel.")
    else:
        print("No data extracted. Check selectors and page structure.")

if __name__ == '__main__':
    crawl()
