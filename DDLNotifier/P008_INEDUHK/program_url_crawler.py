import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl():
    url = "https://www.ln.edu.hk/sgs/taught-postgraduate-programmes/programme-on-offer"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all("div", class_="box16 programe_row_1")
    for index, elem in enumerate(elements[:5]):
        print(f"Element {index + 1} HTML: {elem.prettify()}")
    data = {"ProgramName": [], "URL Link": []}
    for element in elements:
        program_name_tag = element.find("h5")
        link_element = element.find("a", href=True)
        if program_name_tag and link_element:
            program_name = program_name_tag.get_text().strip()
            url_link = "https://www.ln.edu.hk" + link_element["href"]
            # Print the program name and URL link for debugging
            print(f"Program Name: {program_name}, URL: {url_link}")
            # Add information to the DataFrame
            data["ProgramName"].append(program_name)
            data["URL Link"].append(url_link)
    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)

if __name__ == "__main__":
    crawl()
