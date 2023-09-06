import re
import time
import requests
from bs4 import BeautifulSoup
from config.program_details_header import header

from tools.general import request_with_retry
from .base_spider import BaseProgramURLCrawler, BaseProgramDetailsCrawler
from urllib.parse import urljoin

EDINBURGH_BASE_URLS = [
    "https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/taught",
    "https://www.ed.ac.uk/studying/postgraduate/degrees/index.php?r=site/research"
]



class EDProgramURLCrawler(BaseProgramURLCrawler):
    def __init__(self, verbose=True):
        super().__init__(base_url=None, Uni_ID="ED", Uni_name="The University of Edinburgh", verbose=verbose)
        self.base_urls = EDINBURGH_BASE_URLS

    def crawl(self):
        if self.verbose:
            print(f"crawling program urls for {self.Uni_name}...")
        program_words = self._load_program_words()
        program_url_pairs = {}

        for base_url in self.base_urls:
            soup = self._fetch_html(base_url)
            partial_program_url_pairs = self._parse_programs(
                soup, program_words)

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
        super().__init__(Uni_ID="ED",Uni_name="The University of Edinburgh", test=test, verbose=verbose)

    def get_backgroud_requirements(self, soup, program_details, extra_data=None):
        '''
        As of 2023-09-06, Entry requirements is still for 2023/24 academic year,
        there is a paragraph stating "These entry requirements are for the 2023/24 academic year and requirements for future academic years may differ. Entry requirements for the 2024/25 academic year will be published on 2 October 2023." at the start
        '''
        combined_text = ""
        program_entry_req = soup.find(id="proxy_collapseentry_req")
        # Loop through the children of the 'div' tag to find the 'p' elements
        if program_entry_req:
            panel_body_tag = program_entry_req.find(
                'div', {'class': 'panel-body'})
            for child in panel_body_tag.children:
                # Break if we encounter the 'h3' with "Students from China"
                if child.string == 'Students from China':
                    break
                # Add the 'p' element to the list
                if child.name == 'p':
                    combined_text += child.get_text().lower() + " "
                if child.name == 'h4' or child.name == 'h3':
                    combined_text += "\n" + child.get_text().lower() + ": \n" 
                if child.name == 'ul':
                    for li in child.find_all('li'):  # Loop through list items
                        for p in li.find_all('p'):  # Loop through p tags inside list items
                            combined_text += p.get_text().lower() + " "
                if child.name == 'a':
                    link_text = child.string if child.string else 'Link'
                    link_href = child['href'] if 'href' in child.attrs else '#'
                    combined_text += f'[{link_text.lower()}]({link_href}) '  # Markdown format
            program_details[header.background_requirements] = combined_text
        else:
            program_details[header.background_requirements] = "未找到Entry requirements标签"

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        # 定位到程序结构所在的div标签
        structure_div = soup.find('div', id='proxy_collapsehow_taught')

        if structure_div:
            # 提取除<ul>外的所有文本作为课程介绍
            course_intro_texts = [p.get_text()
                                  for p in structure_div.find_all('p')]
            course_intro = '\n'.join(course_intro_texts).strip()
            program_details[header.course_description_english] = course_intro

            # 提取所有<li>标签的文本内容
            course_list_texts = [li.get_text()
                                 for li in structure_div.find_all('li')]
            course_list = '\n - '.join(course_list_texts).strip()
            if course_list:
                course_list = '- ' + course_list  # Add the '-' before the first item
            program_details[header.course_list_english] = course_list
        else:
            program_details[header.course_description_english] = "信息不可用"
            program_details[header.course_list_english] = "信息不可用"

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

    def get_period(self, soup, program_details, extra_data=None):
        # 正则表达式模式
        patterns = [
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine)-years?)',
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine) years?)',
            r'(?:(?:\d+)-years?)',
            r'(?:(?:\d+) years?)',
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)-mths?)',
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) mths?)',
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)-months?)',
            r'(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) months?)',
            r'(?:(?:\d+)-mths?)',
            r'(?:(?:\d+) mths?)',
            r'(?:(?:\d+)-months?)',
            r'(?:(?:\d+) months?)',
        ]

        # 提取extra_data中的所有文本内容
        content_matches = re.findall(r'<[^>]+>([^<]+)<', extra_data)
        all_content = ' '.join(content_matches)

        matched_sentences = []
        primary_period = None

        for pattern in patterns:
            for sentence in re.split(r'[.;!\n]', all_content):
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    if not primary_period:
                        primary_period = match.group()
                    matched_sentences.append(sentence.strip())

        # 若有重复项，利用集合去除重复项
        matched_sentences = list(set(matched_sentences))

        # 将主要时长放在前面
        if primary_period:
            result = primary_period + '. ' + '. '.join(matched_sentences) + '.'
        else:
            result = '. '.join(matched_sentences) + '.'

        program_details[header.course_duration_1] = result

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        program_details[header.admission_month_1] = "9"

    '''
    有很多的tuition fee这里都为空，需要注意
    '''

    def get_tuition(self, soup, program_details, extra_data=None):

        link_tag = soup.find('a',
                             href=re.compile(r'^http://www\.ed\.ac\.uk/studying/postgraduate/fees\?programme_code='))
        if not link_tag:
            tuition_regex = re.compile(
                r'<h3>Tuition fees</h3>(.*?)<h2', re.DOTALL)
            content_match = tuition_regex.search(str(soup))

            if content_match:
                content = content_match.group(1)

                # Match content between tags
                texts = re.findall(r'>\s*([^<]+)\s*<', content)

                # Match https links
                links = re.findall(r'https://[^\s"]+', content)

                # Combine results
                combined_results = '; '.join(
                    [text for text in (texts + links) if text.strip()])

                program_details[header.course_fee] = combined_results.strip()
                return
            else:
                program_details[header.course_fee] = "信息不可用 Tuition Fees/fees找不到，也没有项目专用的学费链接"
                return

        url = link_tag['href']

        response = requests.get(url)
        if response.status_code != 200:
            program_details[header.course_fee] = "该项目未显示，链接请求失败"
            return

        response_soup = BeautifulSoup(response.text, 'html.parser')
        tuition_div = response_soup.find(
            'div', {'class': 'region-content', 'itemprop': 'mainContentOfPage'})
        if tuition_div:
            tuition_text = tuition_div.get_text(strip=True, separator='\n')
            program_details[header.course_fee] = tuition_text
        else:
            program_details[header.course_fee] = "存在项目学费链接，但该项目未显示学费"

    def get_language_requirements(self, soup, program_details, extra_data=None):
        # 查找包含IELTS的abbr标签
        html_content = extra_data

        # Create a regex pattern to find the IELTS information and extract overall and component scores
        pattern = r'<abbr title="International English Language Testing System">IELTS<\/abbr> Academic: total (\d+\.\d+) with at least (\d+\.\d+) in each component.<\/li>'

        # Use re.search to find matches
        match = re.search(pattern, html_content)

        if match:
            overall_score = match.group(1)  # Extract overall score
            component_score = match.group(2)  # Extract component score

            # Round down the component score to an integer (if needed)
            component_score_int = int(float(component_score))

            # Create the new formatted string
            formatted_string = f"总分{overall_score}，小分{component_score_int}"
            program_details[header.ielts_requirement] = formatted_string
        else:
            program_details[header.ielts_requirement] = "信息不可用"
        
    def get_program_description(self, soup, program_details, extra_data=None):
        # 定位到程序描述所在的div标签
        description_div = soup.find('div', id='proxy_collapseprogramme')

        if description_div:
            # 提取div标签内的所有文本
            description_text = description_div.get_text(
                separator='\n', strip=True)
            program_details[header.project_intro] = description_text
        else:
            program_details[header.project_intro] = "信息不可用"

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

        program_details[header.college] = combined_info if combined_info else "信息不可用"

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

        combined_text = ""
        # 搜索包含这些关键词的<p>标签
        program_description = soup.find(id="proxy_collapseprogramme")
        if program_description:
            for p_tag in program_description.find_all('p'):
                combined_text += p_tag.get_text().lower() + " "

        if program_details[header.background_requirements] != "未找到Entry requirements标签":
            combined_text += program_details[header.background_requirements].lower()
        
        combined_text = self.extract_relevant_text(combined_text, keywords)


        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details[header.exam_requirements] = self.judge_interview_preference(
                combined_text)
            program_details[header.exam_requirements_details] = combined_text
        else:
            program_details[header.exam_requirements] = "未要求"

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
        combined_text = ""

        if program_details[header.background_requirements] != "未找到Entry requirements标签":
            combined_text += program_details[header.background_requirements].lower()
        
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.portfolio] = self.judge_portfolio_preference(
                    combined_text)
                program_details[header.portfolio_details] = combined_text
            else:
                program_details[header.portfolio] = "未要求"
        else:
            program_details[header.portfolio] = "未找到Entry requirements标签"

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

        combined_text = ""

        if program_details[header.background_requirements] != "未找到Entry requirements标签":
            combined_text += program_details[header.background_requirements].lower()
    
            combined_text = self.extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.work_experience_years] = self.judge_wrk_exp_preference(
                    combined_text)
                program_details[header.work_experience_details] = combined_text
            else:
                program_details[header.work_experience_years] = "未要求"
        else:
            program_details[header.work_experience_years] = "未找到Entry requirements标签"

    def is_conditional_upper_second(self, text):
        phrases = ["consider a uk 2:2", "may also consider applicants with a uk 2:1 or 2:2","a uk 2:2 honours degree with a strong personal statement"] 

        return any(phrase in text for phrase in phrases)

    def is_upper_second_class(self, text):
        upper_2nd_phrases = ["upper second-class",
                             "upper second class",
                             "upper-second class",
                             "1st class",
                             "first class",
                             "a good 2.1",
                             "2:1 or equivalent",
                             "dental qualification",
                             "a uk 2:1 honours degree",
                             "uk first-class"
                             ]
        return any(phrase in text for phrase in upper_2nd_phrases)

    def is_second_class(self, text):
        second_phrases = ["lower second-class",
                          "lower second class",
                          "lower-second class",
                          "good second class",
                          "a second class",
                          "a second-class",
                          "2:2 or equivalent"
                          ]
        return any(phrase in text for phrase in second_phrases)

    def get_major_requirements_for_uk_students(self, soup, program_details, extra_data=None):
        if program_details[header.background_requirements] != "未找到Entry requirements标签":
            text = program_details[header.background_requirements].lower()
            if self.is_conditional_upper_second(text):
                program_details[header.local_requirements_display] = "有条件2:2"
                return
            elif self.is_upper_second_class(text):
                program_details[header.local_requirements_display] = "2:1"
                return
            elif self.is_second_class(text):
                program_details[header.local_requirements_display] = "2:2"
                return
            else:
                program_details[header.local_requirements_display] = "未要求"
        else:
            program_details[header.local_requirements_display] = "未找到Entry requirements标签"
