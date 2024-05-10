import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

def crawl(url="https://warwick.ac.uk/study/postgraduate/courses/"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # The base URL should end with a slash to ensure urljoin appends the relative path correctly.
    base_url = "https://warwick.ac.uk/study/postgraduate/courses/"

    course_links = soup.select('div.sb-glossary-terms a')
    data = {'ProgramName': [], 'URL Link': []}

    for link in course_links:
        if 'href' in link.attrs:  # Check if the 'href' attribute exists
            program_name = link.get_text(strip=True)
            program_link = link['href']
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
