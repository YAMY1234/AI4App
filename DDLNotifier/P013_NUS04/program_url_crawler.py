import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from DDLNotifier.utils.get_request_header import WebScraper

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')

def crawl(url="https://www.comp.nus.edu.sg/programmes/#mcomp"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers)
    response_text = response.text

    if response.status_code != 200:
        print("网页获取失败，URL不正确！！")
    elif "ROBOT" in response_text or "robot" in response_text:
        webScraper = WebScraper()
        response_text = webScraper.get_html(url)

    # Extract all <a> tags with 'href' attribute from the parsed HTML
    soup = BeautifulSoup(response_text, "html.parser")
    # Extract all <a> tags with 'href' attribute that match the specified class
    a_tags = soup.find_all('a', href=True,
                           class_='eael-creative-button eael-creative-button--wayra')

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
