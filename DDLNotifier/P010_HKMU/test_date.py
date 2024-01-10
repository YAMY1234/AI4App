import requests
from bs4 import BeautifulSoup

def extract_dates_from_hkmu():
    url = "https://admissions.hkmu.edu.hk/sc/tpg/online-application/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting specific parts of the webpage
    extracted_text = []

    # Extracting the dates for the first table
    table1_texts = soup.select('.jet-table__body-row.elementor-repeater-item-27f0b06 .jet-table__cell-text')
    for text in table1_texts:
        extracted_text.append(text.get_text(strip=True))

    # Extracting the dates for the second table
    table2_texts = soup.select('.jet-table__body-row.elementor-repeater-item-27f0b06 .jet-table__cell-text')
    for text in table2_texts:
        extracted_text.append(text.get_text(strip=True))

    return '\n'.join(extracted_text)

# Calling the function and printing the result
extracted_dates = extract_dates_from_hkmu()
print(extracted_dates)