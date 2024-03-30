import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(url="https://law.nus.edu.sg/prospective-students/"):
    webScraper = WebScraper()  # Using the WebScraper class
    response_text = webScraper.get_html(url)

    soup = BeautifulSoup(response_text, "html.parser")

    # Locate the exact span containing "Coursework Programmes"
    coursework_heading = soup.find(lambda tag: tag.name == "span" and "Coursework Programmes" in tag.text)
    if coursework_heading:
        coursework_section = coursework_heading.find_next('ul')
    else:
        return "Coursework Programmes section not found."

    program_links = []
    if coursework_section:
        for li_tag in coursework_section.find_all('li'):
            a_tag = li_tag.find('a')
            if not a_tag:
                continue  # Skip if no <a> tag is present

            program_name = a_tag.text.strip()
            program_link = a_tag['href']

            # Check if there is an abbreviation or extra text in the <li> tag
            extra_text = li_tag.text.strip()[len(program_name):].strip()
            if extra_text:
                program_name += f" {extra_text}"

            # Exclude specific links
            if "Graduate Diploma" in program_name or "Graduate Coursework Certificates" in program_name:
                continue  # Skip this link

            # Collect the program details
            program_links.append({
                "ProgramName": program_name,
                "URL Link": program_link
            })

    # Convert the list of links to a pandas DataFrame
    program_links_df = pd.DataFrame(program_links)

    # Save the DataFrame to an Excel file, excluding the index
    program_links_df.to_excel("programs.xlsx", index=False)

    return program_links_df


# 运行爬虫
if __name__ == "__main__":
    crawl()
