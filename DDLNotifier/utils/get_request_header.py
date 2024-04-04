from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebScraper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # self.service = Service(
        #     executable_path='/root/AI4App/chromedriver-linux64/chromedriver')
        self.service = Service()
        self.options = options
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def get_html(self, url):
        driver = self.driver
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_source = driver.page_source
        return html_source

    def get_cookies(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        cookies = self.driver.get_cookies()
        return cookies

    @staticmethod
    def format_cookies_for_request_header(cookies):
        cookie_parts = [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
        cookie_header = "; ".join(cookie_parts)
        return cookie_header

    def get_cookie_string(self, url):
        cookies = self.get_cookies(url)
        cookie_str = self.format_cookies_for_request_header(cookies)
        return cookie_str

if __name__ == "__main__":
    scraper = WebScraper()
    url = "https://bschool.nus.edu.sg/"
    cookie_str = scraper.get_cookie_string(url)
    print(cookie_str)
