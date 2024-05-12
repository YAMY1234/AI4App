from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin
from DDLNotifier.utils.get_request_header import WebScraper

def crawl(url="https://www.southampton.ac.uk/courses/postgraduate?keyword_filter="):
    webScraper = WebScraper()
    response_text = webScraper.get_html(url)
    soup = BeautifulSoup(response_text, 'html.parser')

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

if __name__ == '__main__':
    crawl()

