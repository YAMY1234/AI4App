from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def crawl(url="https://www.southampton.ac.uk/courses/postgraduate?keyword_filter="):
    options = Options()
    options.add_argument('--headless')  # Run in background
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Fetch the page HTML and parse it
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Then check if any are being filtered out by the style attribute
    test_links_filtered = soup.select('li.course-list-item:not([style*="display: none"]) a')
    print(len(test_links_filtered))  # Compare the count with the previous one
    course_links = soup.select('li.course-list-item:not([style*="display: none"]) a')

    data = {'ProgramName': [], 'URL Link': []}
    base_url = "https://www.southampton.ac.uk"

    for link in course_links:
        program_name = link.find('h3', class_='card-title').text.strip() if link.find('h3', class_='card-title') else 'No Program Name'
        program_link = link.get('href')
        full_url = urljoin(base_url, program_link)  # Properly form the full URL

        data['ProgramName'].append(program_name)
        data['URL Link'].append(full_url)

    if data['ProgramName']:
        PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
        df = pd.DataFrame(data)
        df.to_excel(PROGRAM_DATA_EXCEL, index=False)
        print(f"Data successfully saved to Excel. Total programs found: {len(data['ProgramName'])}")
    else:
        print("No data extracted. Check selectors and page structure.")
    driver.quit()

if __name__ == '__main__':
    crawl()
