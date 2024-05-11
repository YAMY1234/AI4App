from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://www.manchester.ac.uk/study/masters/courses/list/"):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    driver = webdriver.Chrome(options=options)

    # Fetch the webpage
    driver.get(url)
    # Allow some time for JavaScript to execute
    driver.implicitly_wait(10)

    # Get the page source and close the browser
    html = driver.page_source
    driver.quit()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    course_list = soup.find('ul', class_='course-list postgraduate')
    if not course_list:
        print("The expected course list was not found on the page.")
        return

    course_items = course_list.find_all('li', id=True)
    if not course_items:
        print("No course items found within the course list.")
        return

    data = {"ProgramName": [], "URL Link": []}

    for item in course_items:
        title_div = item.find('div', class_='title')
        if title_div and title_div.find('a'):
            program_name = title_div.find('a').get_text(strip=True)
            program_link = urljoin(url, title_div.find('a')['href'])
            data["ProgramName"].append(program_name)
            data["URL Link"].append(program_link)
            print(f"Added program: {program_name}, URL: {program_link}")
        else:
            print(f"Failed to find program details in item with ID: {item['id']}")

    if not data["ProgramName"]:
        print("No programs were added to the list.")
        return

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)
    print(f"Data successfully saved to Excel: {PROGRAM_DATA_EXCEL}")


if __name__ == '__main__':
    crawl()
