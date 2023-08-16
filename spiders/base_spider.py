import os
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook, Workbook
import concurrent.futures


class BaseProgramURLCrawler:
    def __init__(self, base_url, school_name):
        self.base_url = base_url
        self.data_folder = "data"
        self.school_name = school_name
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def crawl(self):
        program_words = self._load_program_words()
        soup = self._fetch_html(self.base_url)
        program_url_pairs = self._parse_programs(soup, program_words)
        self._store_results(program_url_pairs)

    def _load_program_words(self):
        # This can be modified if the source file name or structure changes
        wb = load_workbook(os.path.join(self.data_folder, 'program_word_bank.xlsx'))
        sheet = wb.active
        return [row[0].lower() for row in sheet.iter_rows(min_row=2, values_only=True)]

    def _fetch_html(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def _parse_programs(self, soup, program_words):
        raise NotImplementedError("Each specific crawler should implement this method!")

    def _store_results(self, program_url_pairs):
        school_name = self.school_name
        school_data_folder = os.path.join(self.data_folder, school_name)

        if not os.path.exists(school_data_folder):
            os.makedirs(school_data_folder)

        # Create a new workbook and worksheet
        new_wb = Workbook()
        new_ws = new_wb.active
        new_ws.title = "Program URLs"

        # Add header row
        new_ws.append(["Program Name", "URL"])

        # Store the results in the excel sheet
        for program_name, url in program_url_pairs.items():
            new_ws.append([program_name, url])

        # Save the file
        new_wb.save(os.path.join(school_data_folder, 'program_url_pair.xlsx'))




class BaseProgramDetailsCrawler:

    def __init__(self, school_name):
        self.school_name = school_name

    def read_excel(self, path):
        return load_workbook(path)

    def get_program_useful_links(self):
        wb = self.read_excel(f'data/{self.school_name}/program_url_pair.xlsx')
        sheet = wb.active

        new_wb = Workbook()
        new_sheet = new_wb.active
        new_sheet.append(['项目名','项目链接' ,'项目简介', '链接'])

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(self.process_row, sheet.iter_rows(min_row=2, values_only=True), chunksize=1))

        for result in results:
            new_sheet.append(result)

        new_wb.save(f'data/{self.school_name}/program_useful_link.xlsx')

    def process_row(self, row):
        link_bank = self.read_excel('data/url_bank.xlsx').active
        program_name, url = row

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        intro_div = soup.find('div', class_='zero')
        intro_text = intro_div.get_text() if intro_div else ""

        useful_links = []
        for link in soup.find_all('a'):
            link_name = link.get_text().strip()
            link_url = link.get('href')

            for bank_row in link_bank.iter_rows(min_row=2, values_only=True):
                if bank_row[0].lower() in link_name.lower():
                    useful_links.append(f'{link_name}:{link_url}')
                    break

        return [program_name, url, intro_text] + useful_links

    def scrape_program_details(self):
        # 从 program_detail_headers.txt 读取标题
        with open('data/program_detail_headers.txt', 'r', encoding='utf-8') as file:
            headers = [line.strip() for line in file.readlines()]

        wb = self.read_excel(f'./data/{self.school_name}/program_useful_link.xlsx')
        sheet = wb.active

        new_wb = Workbook()
        new_sheet = new_wb.active
        new_sheet.append(headers)

        # one row is one program
        for row in sheet.iter_rows(min_row=2, values_only=True):
            program_name, program_url, intro_text, *useful_links = row
            program_details = {}
            self.get_data_from_main_url(program_url, program_details)
            self.get_data_from_url(useful_links, program_details)

            # 根据 headers 生成要追加的行
            data_row = [program_details.get(header, '') for header in headers]
            new_sheet.append(data_row)

        new_wb.save(f"./data/{self.school_name}_program_details.xlsx")

    def get_data_from_main_url(self, program_url, program_details):
        response = requests.get(program_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)
        self.get_deadlines(soup, program_details)

        pass

    def get_data_from_url(self, useful_links, program_details):
        # Here you can add more methods to process the soup based on the type of link_name.

        for link in useful_links:
            link_name, url = link.split(':')
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Assuming you will have methods like 'get_deadlines' to process the soup.
            # For example:
            # if "deadline" in link_name.lower():
            #     self.get_deadlines(soup, program_details)

    # Add your methods like get_deadlines, get_language_requirements, etc...
    def get_application_deadlines(self, soup, program_details):
        pass

    def get_backgroud_requirements(self):
        pass

    def get_course_intro_and_details(self):
        pass

    def get_enrollment_deadlines(self):
        pass

    def get_tuition(self):
        pass

    def get_campus(self):
        pass

    def get_language_requirements(self):
        pass

    def get_work_experience_requirements(self):
        pass

    def get_portfolio_requirements(self):
        pass

    def get_GRE_GMAT_requirements(self):
        pass

    def get_major_requirements_for_local_students(self):
        pass

    def British_local_requirements_for_display(self):
        pass

    def get_major_specifications(self):
        pass
