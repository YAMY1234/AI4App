import re
import time
import requests
from bs4 import BeautifulSoup
from config.program_details_header import header

from tools.general import request_with_retry
from .base_spider import BaseProgramURLCrawler, BaseProgramDetailsCrawler

GLA_BASE_URL = "https://www.gla.ac.uk/postgraduate/taught/"


class GLAProgramURLCrawler(BaseProgramURLCrawler):
    def __init__(self, verbose=True):
        super().__init__(base_url=GLA_BASE_URL, Uni_ID="GLA",
                         Uni_name="University of Glasgow", verbose=verbose)

    # Override any method if GLA's site has a different structure or logic
    def _parse_programs(self, soup, _):
        program_url_pairs = {}

        # Iterate through all 'li' items with the specified attributes
        for item in soup.find_all('li'):
            link = item.find('a', href=True)
            if link:
                link_url = link.get('href')
                if '/postgraduate/taught/' not in link_url:
                    continue
                link_url = 'https://www.gla.ac.uk/' + link_url
                # Extract the program name from the link and its next sibling span
                program_name = link.get_text().strip()
                link_name = program_name.replace("[", "").replace("]", "")
                program_url_pairs[link_name] = [link_url, ""]

        return program_url_pairs


class GLAProgramDetailsCrawler(BaseProgramDetailsCrawler):
    def __init__(self, test=False, verbose=True):
        super().__init__(Uni_ID="GLA", test=test, verbose=verbose)
        self.entry_requirements = None

    # Todo: add all rewrite logic here

    def get_language_requirements(self, soup, program_details, extra_data=None):
        # IELTS
        try:
            # Find the IELTS heading
            # print(soup)
            ielts_heading = soup.find('h4', text='International English Language Testing System (IELTS) Academic module (not General Training)')
            
            if ielts_heading is None:
                raise ValueError("IELTS heading not found")

            # Find the next unordered list after the heading
            ul = ielts_heading.find_next('ul')
            
            if ul is None:
                raise ValueError("Unordered list after IELTS heading not found")

            # Find the next unordered list after the heading
            ul = ielts_heading.find_next('ul')
            program_details[header.ielts_remark] = ul.li.text.strip()
        
        except ValueError as e:
            print(e)
        
        # TOEFL
        try:
            # Find the tofel heading
            toefl_heading = soup.find('h4', text='TOEFL (ibt, mybest or athome)')
            
            if toefl_heading is None:
                raise ValueError("TOFEL heading not found")

            # Find the next unordered list after the heading
            ul = toefl_heading.find_next('ul')
            
            if ul is None:
                raise ValueError("Unordered list after tofel heading not found")

            # Find the next unordered list after the heading
            ul = toefl_heading.find_next('ul')
            program_details[header.toefl_remark] = ul.li.text.strip()
        
        except ValueError as e:
            print(e)
        
    def extract_relevant_text(self, text, keywords):
        # Extract sentences containing the phrase from the entry requirements section
        sentences = []
        line_sentences = re.split(r'(?<=[.!?])\s+', text)
        found = False
        for keyword in keywords:
            for sentence in line_sentences:
                if keyword in sentence:
                    sentences.append(sentence)
                    found = True
            # Avoid adding duplicate sentences when multiple keywords are matched
            if found:
                break

        # Combine the extracted sentences into one
        combined_text = ' '.join(sentences).strip()

        return combined_text

    def get_entry_requirements(self, soup):
        # Find the initial <h2> tag
        h2_tag = soup.find('h2', text='Entry requirements')

        # Check if the tag is found
        if h2_tag:
            contents = []
            
            # Traverse through the next sibling tags until we reach the <h3> tag
            for sibling in h2_tag.find_next_siblings():
                # If we reach the <h3> tag, break out of the loop
                if sibling.name == 'h3' and sibling.text == 'English language requirements':
                    break
                contents.append(sibling.text)
            
            # Join the extracted contents to get the desired text
            result = "\n".join(contents)
            self.entry_requirements = result
        else:
            self.entry_requirements = "No entry requirements found"

    def judge_interview_preference(self, text):
        required_phrases = ['may be', 'may also be',
                            'may be considered', 'may also be considered']
        for phrase in required_phrases:
            if phrase in text:
                return "可能要求"
        return "需要"

    def get_interview_requirements(self, soup, program_details, extra_data=None):
        # 定义关键词列表
        keywords = ['interview', 'special qualifying examination', 'qualifying essay',
                    'qualifying assessment', 'written examination', 'oral examination',
                    'oral test', 'required to pass a test', 'written examination', 'written test', 'written assessment']

        if self.entry_requirements is None:
            self.get_entry_requirements(soup)
            
        if self.entry_requirements == "No entry requirements found":
            return
        combined_text = self.entry_requirements.lower()
        
        combined_text = self.extract_relevant_text(combined_text, keywords)


        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details[header.exam_requirements] = self.judge_interview_preference(
                combined_text)
            program_details[header.exam_requirements_details] = combined_text
        else:
            program_details[header.exam_requirements] = "未要求"

    def judge_wrk_exp_preference(self, text):
        required_phrases = ['minimum of', 'at least', 'Ideally', 'is essential', 'must have', 'normally have',
                            'should also have', 'should have', 'need to have']
        for phrase in required_phrases:
            if phrase in text:
                return "需要"
        return "加分项"

    def get_work_experience_requirements(self, soup, program_details, extra_data=None):
        phrases = ['work experience', 'professional experience', 'industrial experience',
                   'existing engineering and design skills', 'practical experience',
                   'experience as a professional', ' who can demonstrate aptitude and experience',
                   'years of relevant experience', 'clinical experience', 'teaching experience',
                   'years\' experience working', 'years of training in',
                   'extensive experience', 'relevant experience',
                   'relevant quantitative or qualitative research experience',
                   'experience working', 'professional involvement',
                   'with equivalent experience', 'industry experience', 'relevant work',
                   'field experience', 'relevant employment']
        if self.entry_requirements is None:
            self.get_entry_requirements(soup)
        if self.entry_requirements == "No entry requirements found":
            return
        combined_text = self.entry_requirements.lower()

        if combined_text:
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.work_experience_years] = self.judge_wrk_exp_preference(
                    combined_text)
                program_details[header.work_experience_details] = combined_text
            else:
                program_details[header.work_experience_years] = "未要求"
        else:
            program_details[header.work_experience_years] = "未找到Entry requirements标签"

    def judge_portfolio_preference(self, text):
        required_phrases = ['may be', 'may also be',
                            'may be considered', 'may also be considered']
        for phrase in required_phrases:
            if phrase in text:
                return "加分项"
        return "需要"

    def get_portfolio_requirements(self, soup, program_details, extra_data=None):
        phrases = ['written work', 'portfolio']
        # program_entry_req = soup.find(id="proxy_collapseentry_req")
        if self.entry_requirements is None:
            self.get_entry_requirements(soup)
        if self.entry_requirements == "No entry requirements found":
            return
        combined_text = self.entry_requirements.lower()

        if combined_text:
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.portfolio] = self.judge_portfolio_preference(
                    combined_text)
                program_details[header.portfolio_details] = combined_text
            else:
                program_details[header.portfolio] = "未要求"
        else:
            program_details[header.portfolio] = "未找到Entry requirements标签"

    def get_period(self, soup, program_details, extra_data=None):
        splash = soup.find(id='prog-key-info-splash')
        if splash:
            # Find all <li> tags
            li_tags = soup.find_all('li')

            # For each <li> tag, check if 'months' is present in the text
            for tag in li_tags:
                if 'months' in tag.text:
                    program_details[header.course_duration_1] = tag.text.strip()

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        splash = soup.find(id='prog-key-info-splash')
        if splash:
            # Find all <li> tags
            li_tags = soup.find_all('li')

            # For each <li> tag, check if 'months' is present in the text
            for tag in li_tags:
                if 'Teaching start:' in tag.text:
                    program_details[header.admission_month_1] = tag.text.strip()

    def get_application_deadlines(self, soup, program_details, extra_data=None):
        h3_tag = soup.find('h3', text='Application deadlines')
        # Initialize a list to store the extracted content
        content_list = []

        if h3_tag is None:
            program_details[header.application_deadlines] = "No application deadlines found"
            return
        
        # Loop through siblings of the h3 tag until you reach the <a> tag
        for sibling in h3_tag.find_next_siblings():
            if sibling.name == 'a':
                break
            content_list.append(str(sibling))

        # Convert the list to a string
        content_str = ''.join(content_list)

        program_details[header.application_deadlines] = content_str

                