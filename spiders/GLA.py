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
                link_url = 'https://www.gla.ac.uk' + link_url
                # Extract the program name from the link and its next sibling span
                program_name = link.get_text().strip()

                # get rid of unwanted program names
                if program_name in ["Taught degree programmes A‑Z", "Contact us"] or "contact" in link_url:
                    continue
                link_name = program_name.replace("[", "").replace("]", "")
                program_url_pairs[link_name] = [link_url, ""]

        return program_url_pairs


class GLAProgramDetailsCrawler(BaseProgramDetailsCrawler):
    def __init__(self, test=False, verbose=True):
        super().__init__(Uni_ID="GLA", test=test, verbose=verbose)
        self.entry_requirements = None

    # Todo: add all rewrite logic here

    # <meta name="description"
    def get_program_description(self, soup, program_details, extra_data=None):
        # 首先，定位到<meta name="description">标签
        meta_description = soup.find('meta', attrs={'name': 'description'})

        if meta_description and meta_description.has_attr('content'):
            # 如果找到了该标签并且它有'content'属性，则提取该属性的内容
            program_details[header.project_intro] = meta_description['content']
        else:
            program_details[header.project_intro] = "没有meta_description内容"

    def get_background_requirements(self, soup, program_details, extra_data=None):
        '''
        <h2 class="alt">Entry requirements</h2>
                <p>2.1 Honours degree or non-UK equivalent in any subject.</p>
        '''
        # 定位到<h2 class="alt">Entry requirements</h2>标签
        h2_tag = soup.find('h2', class_='alt', text='Entry requirements')

        if h2_tag:
            # 从h2标签开始查找，直到找到<h3>English language requirements</h3>
            requirements = []
            current_tag = h2_tag.find_next()
            while current_tag and (current_tag.name != 'h3' and current_tag.name != 'h2'):
                if current_tag.name == 'p':
                    requirements.append(current_tag.get_text(strip=True))
                current_tag = current_tag.find_next()

            if requirements:
                program_details[header.background_requirements] = " ".join(
                    requirements)  # 本来是\n的但是因为只有一段并且避免出现段内换行就直接这样
            else:
                program_details[header.background_requirements] = '信息不可用'
        else:
            program_details[header.background_requirements] = '信息不可用'

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        '''
        <h2 class="alt">Programme structure</h2>
        '''
        # 定位到<h2 class="alt">Programme structure</h2>标签
        h2_tag = soup.find('h2', class_='alt', text='Programme structure')

        if h2_tag:
            # 获取h2_tag之后的所有内容，直到下一个<h2>标签
            subsequent_tags = h2_tag.find_all_next(limit=None)

            # 用于存放<li>标签的文本内容的列表
            li_texts = []

            for tag in subsequent_tags:
                # 如果遇到另一个<h2>标签，停止抓取
                if tag.name == 'h2' and (tag.text != "YEAR 1" or tag.text != "YEAR 2"):
                    break

                # 如果是<li>标签，抓取其文本内容
                if tag.name == 'li':
                    li_texts.append(tag.get_text(strip=True).title())  # .title - 首字母大写，其他字母小写

            # 使用换行符拼接所有<li>标签的文本内容
            program_details[header.course_list_english] = '\n'.join(li_texts)
        else:
            program_details[header.course_list_english] = '信息不可用'

    def extract_requirements_info(self, soup, program_details, extra_data=None):
        # 定位到<h2 class="alt">Entry requirements</h2>标签
        h2_tag = soup.find('h2', class_='alt', text='Entry requirements')
        if not h2_tag:
            program_details[header.cn_requirement] = "未找到Entry requirements标签"
            program_details[header.uk_requirement] = "未找到Entry requirements标签"
            return

        # 获取h2_tag之后的所有内容，直到下一个<h2>标签
        subsequent_tags = h2_tag.find_all_next()

        texts = []
        for tag in subsequent_tags:
            # 如果遇到另一个<h2>标签，停止抓取
            if tag.name == 'h2':
                break
            texts.append(tag.get_text(strip=True))

        program_details[header.cn_requirement] = "2:1"
        program_details[header.uk_requirement] = "2:1"
        # 通过正则表达式查找2:1和2:2的条件
        for text in texts:
            text_lower = text.lower()
            if re.search(r'2\.1|2:1', text_lower):
                program_details[header.cn_requirement] = "2:1"
                program_details[header.uk_requirement] = "2:1"
            elif re.search(r'2\.2|2:2', text_lower):
                # 查找"may"、"could"等表示可能性的词汇
                if re.search(r'\b(may|could)\b', text_lower):
                    program_details[header.uk_requirement] = "有条件2:2"
                else:
                    program_details[header.cn_requirement] = "2:2"
                    program_details[header.uk_requirement] = "2:2"

    def get_GRE_GMAT_requirements(self, soup, program_details, extra_data=None):
        # 正则表达式模式

        # 提取extra_data中的所有文本内容
        content_matches = re.findall(r'<[^>]+>([^<]+)<', extra_data)
        all_content = ' '.join(content_matches)

        matched_sentences = []
        pattern = r'GRE(?![A-Z])'  # 查找包含大写"GRE"的片段，并确保后面不紧跟大写字母
        matched_sentences = []

        for sentence in re.split(r'[.;!\n]', all_content):
            if re.search(pattern, sentence):
                matched_sentences.append(sentence.strip())

        result = '. '.join(matched_sentences) + '.' if matched_sentences else "官网没有明确说明"
        program_details[header.gre] = result

        pattern = r'GMAT(?![A-Z])'  # 查找包含大写"GMAT"的片段
        matched_sentences = []
        for sentence in re.split(r'[.;!\n]', all_content):
            if re.search(pattern, sentence):
                matched_sentences.append(sentence.strip())
        result = '. '.join(matched_sentences) + '.' if matched_sentences else "官网没有明确说明"
        program_details[header.gmat] = result

    def get_major_requirements_for_chinese_students(self, soup, program_details, extra_data=None):
        self.extract_requirements_info(soup, program_details, extra_data)

    def get_language_requirements(self, soup, program_details, extra_data=None):
        # IELTS
        try:
            # Find the IELTS heading
            ielts_text = 'International English Language Testing System (IELTS)'
            ielts_heading = soup.find('h4', string=lambda x: x and (ielts_text in x or x.startswith(ielts_text)))

            if ielts_heading is None:
                program_details[header.ielts_remark] = "IELTS heading not found"
                raise ValueError("IELTS heading not found")

            # Find the next unordered list after the heading
            ul = ielts_heading.find_next('ul')

            if ul is None:
                program_details[header.ielts_remark] = "Unordered list after IELTS heading not found"
                raise ValueError("Unordered list after IELTS heading not found")

            program_details[header.ielts_remark] = ul.li.text.strip()

            pattern = r'(\d+\.\d+)'

            matches = re.findall(pattern, program_details[header.ielts_remark])
            if len(matches) > 1:
                overall_score = matches[0]
                sub_scores = matches[1]
                program_details[header.ielts_requirement] = f"总分{overall_score}，小分{sub_scores}"
            else:
                program_details[header.ielts_requirement] = f"信息不可用"

        except ValueError as e:
            print(e)

        # TOEFL
        try:
            # Find the tofel heading
            toefl_heading = soup.find('h4', text='TOEFL (ibt, mybest or athome)')

            if toefl_heading is None:
                program_details[header.toefl_remark] = "TOFEL heading not found"
                raise ValueError("TOFEL heading not found")

            # Find the next unordered list after the heading
            ul = toefl_heading.find_next('ul')

            if ul is None:
                program_details[header.toefl_remark] = "Unordered list after tofel heading not found"
                raise ValueError("Unordered list after tofel heading not found")

            # Find the next unordered list after the heading
            ul = toefl_heading.find_next('ul')
            program_details[header.toefl_remark] = ul.li.text.strip()

        except ValueError as e:
            print(e)

    def _extract_relevant_text(self, text, keywords):
        # Extract sentences containing the phrase from the entry requirements section
        sentences = []

        # Adjust the split logic to avoid splitting at points like '(approx. 2,000 words)'
        line_sentences = re.split(r'(?<=[.!?])(?!\s*[\)])\s+', text)
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

    def _judge_interview_preference(self, text):
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

        combined_text = self._extract_relevant_text(combined_text, keywords)

        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details[header.exam_requirements] = self._judge_interview_preference(
                combined_text)
            program_details[header.exam_requirements_details] = combined_text
        else:
            program_details[header.exam_requirements] = "未要求"

    def _judge_wrk_exp_preference(self, text):
        required_phrases = ["may", "preferably", 'minimum of', 'at least', 'Ideally', 'is essential', 'must have',
                            'normally have',
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
            combined_text = self._extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.work_experience_years] = self._judge_wrk_exp_preference(
                    combined_text)
                program_details[header.work_experience_details] = combined_text
            else:
                program_details[header.work_experience_years] = "未要求"
        else:
            program_details[header.work_experience_years] = "未找到Entry requirements标签"

    def _judge_portfolio_preference(self, text):
        required_phrases = ["may", "preferably", 'may be', 'may also be',
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
            combined_text = self._extract_relevant_text(combined_text, phrases)
            if combined_text:
                program_details[header.portfolio] = self._judge_portfolio_preference(
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

            # Define the regex pattern
            pattern = r'(\d+)\s*(year|month)'

            # For each <li> tag, check if 'months' or 'year' is present in the text
            for tag in li_tags:
                match = re.search(pattern, tag.text)
                if match:
                    number = match.group(1)
                    unit = match.group(2)

                    # Convert the text to desired format
                    if "year" in unit:
                        duration = f"{number}年"
                    elif "month" in unit:
                        duration = f"{number}个月"
                    else:
                        continue  # skip if no match

                    program_details[header.course_duration_1] = duration
                    break  # Exit once we've found and processed a match

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        def month_to_number(month_str):
            months = {
                'January': 1,
                'February': 2,
                'March': 3,
                'April': 4,
                'May': 5,
                'June': 6,
                'July': 7,
                'August': 8,
                'September': 9,
                'October': 10,
                'November': 11,
                'December': 12
            }
            return months.get(month_str.strip(), None)

        splash = soup.find(id='prog-key-info-splash')
        if splash:
            # Find all <li> tags
            li_tags = soup.find_all('li')

            # For each <li> tag, check if 'Teaching start:' is present in the text
            for tag in li_tags:
                if 'Teaching start:' in tag.text:
                    months_str = tag.text.strip().split(':')[1]
                    months = [m.strip() for m in months_str.split('or')]
                    if len(months) > 0:
                        program_details[header.admission_month_1] = month_to_number(months[0])
                    if len(months) > 1:
                        program_details[header.admission_month_2] = month_to_number(months[1])

    def get_application_deadlines(self, soup, program_details, extra_data=None):
        h3_tag = soup.find('h3', text='Application deadlines')
        # Initialize a list to store the extracted text content
        content_list = []

        if h3_tag is None:
            program_details[header.application_deadlines] = "No application deadlines found"
            return

        # Loop through siblings of the h3 tag until you reach the <a> tag
        for sibling in h3_tag.find_next_siblings():
            if sibling.name == 'a':
                break
            # Instead of adding the entire tag, we just add its text content
            content_list.append(sibling.get_text(strip=True))

        # Convert the list to a string using join.
        # Adding a newline between each content for better readability.
        content_str = '\n'.join(content_list)

        program_details[header.application_deadlines] = content_str

    def get_tuition(self, soup, program_details, extra_data=None):
        # 定位到<h4>International & EU</h4>标签
        h4_tag = soup.find('h4', text='International & EU')

        if h4_tag:
            # 从<h4>标签开始，查找其后的<li>标签
            li_tag = h4_tag.find_next_sibling('ul').find('li') if h4_tag.find_next_sibling('ul') else None

            if li_tag:
                # 提取费用信息（使用正则表达式来确保只提取数字）
                fee = re.search(r'(\d+[,]*\d*)', li_tag.get_text())
                if fee:
                    program_details[header.course_fee] = fee.group(1).replace(',', '')  # 去除逗号
                else:
                    program_details[header.course_fee] = "费用信息不可用"
            else:
                program_details[header.course_fee] = "费用信息不可用"
        else:
            # 格式不一样，所以需要在extra_data当中进行提取
            if extra_data:
                fee_patterns = [
                    r'<p><strong>International:&nbsp;&nbsp;</strong></p>\s*<ul>\s*<li>&pound;(\d+[,]*\d*)&nbsp;',
                    r'<p>UK/EU and non-EU programme countries</p>\s*<ul>\s*<li>\s*&pound;(\d+[,]*\d*)&nbsp;',
                    r'<p><strong>UK/EU and non-EU programme countries&nbsp;</strong></p>\s*<ul>\s*<li><strong>Full time fee</strong>: &pound;(\d{1,3}(?:,\d{3})*)(?=&nbsp;)',
                    r'Full time fee.*?&pound;([\d,]+)',
                    r'Full-time fee.*?&pound;([\d,]+)',
                    r'International students.*?&pound;([\d,]+)',
                ]
                for fee_pattern in fee_patterns:
                    fee_match = re.search(fee_pattern, extra_data)
                    if fee_match:
                        program_details[header.course_fee] = fee_match.group(1).replace(',', '')  # 去除逗号
                        break
                    else:
                        program_details[header.course_fee] = "费用信息不可用"
            else:
                program_details[header.course_fee] = "费用信息不可用"


'''

<p>UK/EU and non-EU programme countries</p>

<ul>
	<li><strong>Full time fee</strong>:&nbsp;&pound;9,000&nbsp;per annum or&nbsp;&euro;10,178&nbsp;per annum</li>
</ul>


<p><strong>Fees for the 2 year programme:</strong></p>

<p><strong>International:&nbsp;&nbsp;</strong></p>

<ul>
	<li>&pound;18,060&nbsp;per annum</li>
</ul>


'''
