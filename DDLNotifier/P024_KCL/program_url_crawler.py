from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(base_url="https://www.kcl.ac.uk/search/courses"):
    options = Options()
    options.add_argument('--headless')  # Run in background
    driver = webdriver.Chrome(options=options)

    data = {"ProgramName": [], "URL Link": []}
    page = 0

    while True:
        url = f"{base_url}?coursesPage={page}&level=postgraduate-taught"
        print(f"Fetching data from: {url}")
        driver.get(url)

        # Let's print the current page HTML to inspect it
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        courses = soup.find_all('div', class_='Cardstyled__CardStyled-sc-147a7mv-0 kymBik')
        if not courses:
            print("No more courses found or page did not load as expected at: {url}")
            break  # Break if no courses are found or if the page fails to load expected content

        print(f"Found {len(courses)} courses on page {page + 1}.")

        for course in courses:
            link_tag = course.find('a', class_='wrapper-link')
            title_tag = course.find('h3', class_='Headingstyled__DynamicHeading-sc-1544wc-0')
            badges = course.find_all('div', class_='CardBadgestyled__CardBadgeStyled-sc-1ib578y-0 gnVOIV')

            if badges and any("Full time" in badge.get_text() for badge in badges):
                program_name = title_tag.get_text(strip=True) if title_tag else 'N/A'
                program_link = link_tag['href'] if link_tag else 'N/A'

                data["ProgramName"].append(program_name)
                data["URL Link"].append(program_link)

                print(f"Added program: {program_name} with URL: {program_link}")

        page += 1  # Increment the page number for the next iteration

    driver.quit()

    if not data["ProgramName"]:
        print("No programs were added to the list.")
        return

    df = pd.DataFrame(data)
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)
    print(f"Data successfully saved to Excel: {PROGRAM_DATA_EXCEL}")


if __name__ == '__main__':
    crawl()
