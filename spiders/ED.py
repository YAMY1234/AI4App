import re
import time
import requests
from bs4 import BeautifulSoup

from tools.general import request_with_retry
from .base_spider import BaseProgramURLCrawler, BaseProgramDetailsCrawler
from urllib.parse import urljoin

EDINBURGH_BASE_URLS = [
    "https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/taught",
    "https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/research"
]


class EDProgramURLCrawler(BaseProgramURLCrawler):
    def __init__(self):
        super().__init__(base_url=None, school_name="ED")
        self.base_urls = EDINBURGH_BASE_URLS

    def crawl(self):
        program_words = self._load_program_words()
        program_url_pairs = {}

        for base_url in self.base_urls:
            soup = self._fetch_html(base_url)
            partial_program_url_pairs = self._parse_programs(soup, program_words)

            # Merging dictionaries
            program_url_pairs.update(partial_program_url_pairs)

        self._store_results(program_url_pairs)

    def _parse_programs(self, soup, _):
        program_url_pairs = {}

        for link in soup.find_all('a', href=True):
            link_url = link.get('href')
            link_name = link.get_text().strip().lower()

            # Check if the URL starts with one of the base URLs
            if "id=" in link_url:
                link_url = "https://www.ed.ac.uk" + link_url
                # Try to find the faculty info immediately following the link
                faculty_info = link.find_next_sibling(
                    "span", class_="search-results__dept")
                if faculty_info:
                    program_faculty = faculty_info.get_text().strip()
                else:
                    program_faculty = "N/A"  # Default value in case the faculty info is missing

                program_url_pairs[link_name] = [link_url, program_faculty]

        return program_url_pairs


class EDProgramDetailsCrawler(BaseProgramDetailsCrawler):
    def __init__(self, test=False, verbose=True):
        super().__init__(school_name="ED", test=test, verbose=verbose)

    def get_backgroud_requirements(self, soup, program_details, extra_data=None):
        # Locate the "Programme description" panel
        panel_title = soup.find("h2", class_="panel-title", string="Programme description")
        if not panel_title:
            program_details["相关背景要求"] = "N/A"
            return

        # Navigate to the panel content div
        panel_body = panel_title.find_next_sibling("div", class_="panel-collapse").find("div", class_="panel-body")
        if not panel_body:
            program_details["相关背景要求"] = "N/A"
            return

        # Extract all <p> and <h> tags within the panel content
        texts = []
        for tag in panel_body.children:
            # if isinstance(tag, BeautifulSoup.Tag):  # Ensure we're looking at a tag, not a string
            if tag.name.startswith('p') or tag.name.startswith('h'):
                texts.append(tag.get_text(strip=True))

        # Join the texts to form a single string
        program_details["相关背景要求"] = ' '.join(texts)

        from bs4 import BeautifulSoup

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        # 定位到程序结构所在的div标签
        structure_div = soup.find('div', id='proxy_collapsehow_taught')

        if structure_div:
            # 提取除<ul>外的所有文本作为课程介绍
            course_intro_texts = [p.get_text() for p in structure_div.find_all('p')]
            course_intro = '\n'.join(course_intro_texts).strip()
            program_details['课程介绍英'] = course_intro

            # 提取所有<li>标签的文本内容
            course_list_texts = [li.get_text() for li in structure_div.find_all('li')]
            course_list = '\n - '.join(course_list_texts).strip()
            if course_list:
                course_list = '- ' + course_list  # Add the '-' before the first item
            program_details['课程列表英'] = course_list
        else:
            program_details['课程介绍英'] = "信息不可用"
            program_details['课程列表英'] = "信息不可用"

    '''
    需要修改或实现的函数以及需要添加到的dict的key: def get_period(self, soup, program_details, extra_data=None):  需要添加到：program_details[f"课程时长1(学制)"], 
    
    修改要求: 首先，定位到名为Applying的h2标签，然后在h2标签所在的那一个<div class="col-xs-12">标签当中搜寻其中的文字信息，如果对应的小写匹配的1 year full-timee, 2 year full-time，或者Awards: MSc (12-12 mth FT, 24-24 mth PT)这种的话，那么就填入对应的full-time对应的时间作为答案。 
    
    参考网页代码,
     <h2>Applying</h2>
    
     <p>Select your programme and preferred start date to begin your application.</p><div class="row finderSearch"><div class="col-xs-12"><h5>MSc Accounting and Finance - 1 Year (Full-time)</h5><div class="input-group input-group-lg"><select name="code2" class="form-control" required=""><option value="">Select your start date</option><option value="https://www.star.euclid.ed.ac.uk/public/urd/sits.urd/run/siw_ipp_lgn.login?process=siw_ipp_app&amp;code1=PTMSCACFIN1F&amp;code2=0017">9 September 2024</option></select><span class="input-group-btn"><input type="button" value="Apply" class="btn btn-uoe btn-apply btn-euclid-apply" title="Apply: MSc Accounting and Finance - 1 Year (Full-time)" /></span></div></div></div> </div>
    
     </div>
     BUG:   File "/Users/liyangmin/PycharmProjects/AI4App/spiders/ED.py", line 117, in get_period
        col_div = applying_h2.find_next_sibling("div", class_="row").find("div", class_="col-xs-12")
    AttributeError: 'NoneType' object has no attribute 'find'
    '''

    def get_period(self, soup, program_details, extra_data=None):  # todo: fix the bug above
        # 正则表达式匹配数字和英文年/月
        pattern = r'\b\d+(-\d+)?\s*(years?|months?|yrs?|mths?)\b'

        # 获取soup的全部文本
        text = soup.get_text()

        # 根据句子对文本进行分割
        sentences = re.split(r'[.;!\n]|<[^>]+>', text)
        matched_sentences = []

        for sentence in sentences:
            # 搜索与正则模式匹配的文本
            if re.search(pattern, sentence, re.IGNORECASE):
                matched_sentences.append(sentence.strip())

        # 将匹配的句子合并成字符串
        result = '. '.join(matched_sentences) + '.'
        program_details["课程时长1(学制)"] = result

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        program_details["入学月1"] = "9"

    '''
    有很多的tuition fee这里都为空，需要注意
    '''
    def get_tuition(self, soup, program_details, extra_data=None):

        link_tag = soup.find('a',
                             href=re.compile(r'^http://www\.ed\.ac\.uk/studying/postgraduate/fees\?programme_code='))
        if not link_tag:
            fees_h3 = soup.find('h3', string='Tuition Fees')
            if not fees_h3:
                fees_h3 = soup.find('h3', string='Tuition fees')
            if fees_h3:
                next_h2 = fees_h3.find_next('h3')
                if next_h2:
                    content_between_h2s = ''.join(map(str, list(fees_h3.next_siblings)[:-1]))
                    program_details["课程费用"] = BeautifulSoup(content_between_h2s, 'html.parser').get_text(
                        separator='\n', strip=True)
                else:
                    program_details["课程费用"] = "信息不可用Tuition fees后面没有h2标签"
            else:
                program_details["课程费用"] = "信息不可用 Tuition Fees找不到"
            return

        url = link_tag['href']

        response = requests.get(url)
        if response.status_code != 200:
            program_details["课程费用"] = "该项目未显示，链接请求失败"
            return

        response_soup = BeautifulSoup(response.text, 'html.parser')
        tuition_div = response_soup.find('div', {'class': 'region-content', 'itemprop': 'mainContentOfPage'})
        if tuition_div:
            tuition_text = tuition_div.get_text(strip=True, separator='\n')
            program_details["课程费用"] = tuition_text
        else:
            program_details["课程费用"] = "该项目未显示，不存在该内容"

    def get_language_requirements(self, soup, program_details, extra_data=None):
        h3_tag = soup.find('h3', text='English language requirements')
        if not h3_tag:
            program_details["雅思要求"] = "信息未找到"
            return

        # Find the next h3 or h2 tag
        next_h3_or_h2 = h3_tag.find_next(['h3', 'h2'])

        # Start from h3_tag and iterate until next_h3_or_h2
        element = h3_tag.next_sibling
        while element and element != next_h3_or_h2:
            if element.name == 'li' and 'IELTS' in element.get_text():
                program_details["雅思要求"] = element.get_text().strip()
                return
            element = element.next_sibling

        program_details["雅思要求"] = "信息未找到"

    def get_program_description(self, soup, program_details, extra_data=None):
        # 定位到程序描述所在的div标签
        description_div = soup.find('div', id='proxy_collapseprogramme')

        if description_div:
            # 提取div标签内的所有文本
            description_text = description_div.get_text(separator='\n', strip=True)
            program_details["项目简介"] = description_text
        else:
            program_details["项目简介"] = "信息不可用"

        school_span = soup.find('span', text='School: ')
        college_span = soup.find('span', text='College: ')

        school_info = ""
        college_info = ""

        if school_span:
            school_a = school_span.find_next_sibling()
            if school_a:
                school_info = "School: " + school_a.get_text(strip=True)

        if college_span:
            college_a = college_span.find_next_sibling()
            if college_a:
                college_info = "College: " + college_a.get_text(strip=True)

        # 拼接School和College信息
        combined_info = school_info
        if school_info and college_info:
            combined_info += " | "
        combined_info += college_info

        program_details["学院"] = combined_info if combined_info else "信息不可用"


    def judge_interview_preference(self, text):
        required_phrases = ['may be', 'may also be', 'may be considered', 'may also be considered']
        for phrase in required_phrases:
            if phrase in text:
                return "可能要求"
        return "需要"

    def get_interview_requirements(self, soup, program_details, extra_data=None):
        # 定义关键词列表
        keywords = ['interview', 'special qualifying examination', 'qualifying essay',
                    'qualifying assessment', 'written examination', 'oral examination',
                    'oral test', 'required to pass a test', 'written examination', 'written test', 'written assessment']

        combined_text = ""
        # 搜索包含这些关键词的<p>标签
        program_description = soup.find(id="proxy_collapseprogramme")
        if program_description:
            for p_tag in program_description.find_all('p'):
                combined_text += p_tag.get_text().lower() + " "
        
        program_entry_req = soup.find(id="proxy_collapseentry_req")
        # Loop through the children of the 'div' tag to find the 'p' elements
        if program_entry_req:
            panel_body_tag = program_entry_req.find('div', {'class': 'panel-body'})
            for child in panel_body_tag.children:
                # Break if we encounter the 'h3' with "Students from China"
                if child.name == 'h3' and child.string == 'Students from China':
                    break
                # Add the 'p' element to the list
                if child.name == 'p':
                    combined_text += child.get_text().lower() + " "
            combined_text = self.extract_relevant_text(combined_text, keywords)

        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details["面/笔试要求"] = self.judge_interview_preference(combined_text)
            program_details["面/笔试要求细则"] = combined_text
        else:
            program_details["面/笔试要求"] = "未要求"

    def judge_portfolio_preference(self, text):
        required_phrases = ['may be', 'may also be', 'may be considered', 'may also be considered']
        for phrase in required_phrases:
            if phrase in text:
                return "加分项"
        return "需要"

    def get_portfolio_requirements(self, soup, program_details, extra_data=None):
        phrases = ['written work', 'portfolio']
        program_entry_req = soup.find(id="proxy_collapseentry_req")
        combined_text = ""
        # Loop through the children of the 'div' tag to find the 'p' elements
        if program_entry_req:
            panel_body_tag = program_entry_req.find('div', {'class': 'panel-body'})
            for child in panel_body_tag.children:
                # Break if we encounter the 'h3' with "Students from China"
                if child.name == 'h3' and child.string == 'Students from China':
                    break
                # Add the 'p' element to the list
                if child.name == 'p':
                    combined_text += child.get_text().lower() + " "
            
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details["作品集"] = self.judge_portfolio_preference(
                    combined_text)
                program_details["作品集细则"] = combined_text
            else:
                program_details["作品集"] = "未要求"
        else:
            program_details["作品集"] = "未找到Entry requirements标签"

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

    def judge_wrk_exp_preference(self, text):
        required_phrases = ['minimum of', 'at least', 'Ideally', 'essential', 'must have', 'normally have',
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
                   'experience in', 'experience working', 'professional involvement',
                   'experience of', 'with equivalent experience', 'industry experience', 'relevant work',
                   'field experience', 'relevant employment']
        
        program_entry_req = soup.find(id="proxy_collapseentry_req")
        combined_text = ""
        # Loop through the children of the 'div' tag to find the 'p' elements
        if program_entry_req:
            panel_body_tag = program_entry_req.find('div', {'class': 'panel-body'})
            for child in panel_body_tag.children:
                # Break if we encounter the 'h3' with "Students from China"
                if child.name == 'h3' and child.string == 'Students from China':
                    break
                # Add the 'p' element to the list
                if child.name == 'p':
                    combined_text += child.get_text().lower() + " "
            
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details["工作经验（年）"] = self.judge_wrk_exp_preference(
                    combined_text)
                program_details["工作经验细则"] = combined_text
            else:
                program_details["工作经验（年）"] = "未要求"
        else:
            program_details["工作经验（年）"] = "未找到Entry requirements标签"