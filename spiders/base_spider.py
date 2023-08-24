import json
import os
import threading
import time

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook, Workbook
import concurrent.futures

from tools.general import request_with_retry
from utils.logger import setup_logger


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

    def __init__(self, school_name, test=False):
        self.school_name = school_name
        self.test = test
        if self.test:
            self.useful_link_path = f'data/{self.school_name}/program_useful_link_sample.xlsx'
            self.details_path = f'data/{self.school_name}/program_details_sample.xlsx'
        else:
            self.useful_link_path = f'data/{self.school_name}/program_useful_link.xlsx'
            self.details_path = f'data/{self.school_name}/program_details.xlsx'

    def read_excel(self, path):
        return load_workbook(path)

    def get_program_useful_links(self):
        url_pair_path = f'data/{self.school_name}/program_url_pair.xlsx'
        if self.test:
            url_pair_path = f'data/{self.school_name}/program_url_pair_sample.xlsx'
            # generate a sample based on first 10 rows of program_url_pair.xlsx        
            if not os.path.exists(url_pair_path):
                original_ = f'data/{self.school_name}/program_url_pair.xlsx'
                wb = self.read_excel(original_)
                sheet = wb.active
                new_wb = Workbook()
                new_sheet = new_wb.active
                new_sheet.append(["Program Name", "URL"])
                for row in sheet.iter_rows(min_row=2, max_row=11, values_only=True):
                    new_sheet.append(row)
                new_wb.save(url_pair_path)

        print("reading url pairs from " + url_pair_path)
        wb = self.read_excel(url_pair_path)
        sheet = wb.active

        new_wb = Workbook()
        new_sheet = new_wb.active
        new_sheet.append(['项目名','项目链接' ,'项目简介', '链接'])

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(self.process_row, sheet.iter_rows(min_row=2, values_only=True), chunksize=1))

        for result in results:
            new_sheet.append(result)

        new_wb.save(self.useful_link_path)
        print("useful links saved to " + self.useful_link_path)

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

    def thread_task(self, row, headers, new_sheet, lock):
        program_name, program_url, intro_text, *useful_links = row
        program_details = {}
        program_details["专业"] = program_name
        program_details["官网链接"] = program_url
        program_details["项目简介"] = intro_text

        self.get_data_from_main_url(program_url, program_details)
        # self.get_data_from_url(useful_links, program_details)

        # 根据 headers 生成要追加的行
        data_row = [program_details.get(header, '') for header in headers]
        if self.test:
            print(json.dumps(program_details, indent=4, ensure_ascii=False))
        else:
            print(f"succeeded with program: {program_name}.")

        with lock:  # 确保线程安全
            new_sheet.append(data_row)

    def generate_program_details(self, verbose=True):
        self.scrape_program_details()
        self.write_program_constants()
        if verbose:
            print(f"{self.school_name} updated successfully.")

    def write_program_constants(self):
        # read headers from university_constants.csv
        with open('data/Constants/university_constants.csv', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            # TODO: Only one line in university_constants.csv for now
            headers = lines[0].split(sep=',')
            data = lines[1].split(sep=',')

        # open program_details.xlsx
        wb = self.read_excel(self.details_path)
        sheet = wb.active

        # insert constant headers to program_details.xlsx at the beginning
        for header in reversed(headers):
            sheet.insert_cols(1)
            sheet.cell(row=1, column=1, value=header)
        
        # write constants to program_details.xlsx
        for header in headers:
            for row in range(2, sheet.max_row + 1):
                sheet.cell(row=row, column=headers.index(header) + 1, value=data[headers.index(header)])
            
        # save program_details.xlsx
        wb.save(self.details_path)
        

    def scrape_program_details(self):
        # 从 program_detail_headers.txt 读取标题
        with open('data/program_detail_headers.txt', 'r', encoding='utf-8') as file:
            headers = [line.strip() for line in file.readlines()]

        wb = self.read_excel(self.useful_link_path)
        sheet = wb.active

        new_wb = Workbook()
        new_sheet = new_wb.active
        new_sheet.append(headers)

        lock = threading.Lock()
        threads = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            t = threading.Thread(target=self.thread_task, args=(row, headers, new_sheet, lock))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        new_wb.save(self.details_path)

    def get_data_from_main_url(self, program_url, program_details):
        # try:
        #     response = requests.get(program_url)
        # except requests.ConnectionError as e:
        #     print(f"ConnectionError for URL {program_url}: {e}")
        #     return
        response = request_with_retry(
            url=program_url,
            school_name=self.school_name
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # self.get_program_intro(soup, program_details)
        self.get_backgroud_requirements(soup, program_details)
        self.get_course_intro_and_details(soup, program_details)
        self.get_enrollment_deadlines(soup, program_details)
        self.get_tuition(soup, program_details)
        self.get_period(soup, program_details)
        self.get_language_requirements(soup, program_details)
        self.get_interview_requirements(soup, program_details)
        self.get_work_experience_requirements(soup, program_details)
        self.get_portfolio_requirements(soup, program_details)
        self.get_GRE_GMAT_requirements(soup, program_details)
        self.get_major_requirements_for_chinese_students(soup, program_details)
        self.get_major_requirements_for_uk_students(soup, program_details)


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

    # def get_program_intro(self, soup, program_details, extra_data=None):
    #     program_details["项目简介"] = program_details["项目简介"]

    def get_backgroud_requirements(self, soup, program_details, extra_data=None):
        pass

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        pass

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        pass

    def get_tuition(self, soup, program_details, extra_data=None):
        pass

    def get_period(self, soup, program_details, extra_data=None):
        pass

    def get_language_requirements(self, soup, program_details, extra_data=None):
        pass

    def get_interview_requirements(self, soup, program_details, extra_data=None):
        # 定义关键词列表
        keywords = ['interview', 'qualifying examination', 'qualifying essay',
                    'qualifying assessment', 'written examination', 'oral examination', 'oral test']

        # 搜索包含这些关键词的<p>标签
        matching_paragraphs = []
        for keyword in keywords:
            # matching_paragraphs.extend(soup.find_all('p', string=lambda text: keyword in text.lower()))
            matching_paragraphs.extend(soup.find_all(string=lambda text: keyword in text.lower()))

        # 合并所有匹配的段落的文本内容
        combined_text = ' '.join([p.get_text(strip=True) for p in matching_paragraphs])

        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details["面/笔试要求"] = combined_text
        else:
            program_details["面/笔试要求"] = "未要求"

    def get_work_experience_requirements(self, soup, program_details, extra_data=None):
        pass

    def get_portfolio_requirements(self, soup, program_details, extra_data=None):
        pass

    def get_GRE_GMAT_requirements(self, soup, program_details, extra_data=None):
        pass

    def get_major_requirements_for_chinese_students(self, soup, program_details, extra_data=None):
        pass

    def get_major_requirements_for_uk_students(self, soup, program_details, extra_data=None):
        pass

    def get_major_specifications(self, soup, program_details, extra_data=None):
        pass

    # def get_campus(self, soup, program_details):
    #     pass

    # def British_local_requirements_for_display(self, soup, program_details):
    #     pass

    # def get_application_deadlines(self, soup, program_details):
    #     pass



