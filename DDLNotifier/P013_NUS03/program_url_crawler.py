import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://www.comp.nus.edu.sg/programmes/#mcomp"):
    # Initialize a list to store program links that satisfy the given conditions
    program_links = []
    for a_tag in a_tags:
        link = a_tag['href']
        # Construct the full URL if needed (assuming relative links)
        full_url = f"https://www.comp.nus.edu.sg{link}" if link.startswith(
            '/') else link
        if "programmes" in link and \
                (len(full_url.split('/')) == 7 or len(full_url.split('/')) == 6 and full_url[-1] != '/') and \
                "dmajor" not in full_url and "minor" not in full_url:
            program_name = a_tag.find('span',
                                      class_='cretive-button-text').text.strip()
            program_links.append({
                "ProgramName": program_name,
                "URL Link": full_url
            })

    # Convert the list of dictionaries into a pandas DataFrame
    program_links_df = pd.DataFrame(program_links)

    # Save the DataFrame to an Excel file without the index
    program_links_df.to_excel("programs.xlsx", index=False)


# 运行爬虫
if __name__ == "__main__":
    crawl()
