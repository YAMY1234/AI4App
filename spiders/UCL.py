import re
import time
import requests
from bs4 import BeautifulSoup
from config.program_details_header import header

from tools.general import request_with_retry
from .base_spider import BaseProgramURLCrawler, BaseProgramDetailsCrawler

UCL_BASE_URL = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees"


class UCLProgramURLCrawler(BaseProgramURLCrawler):
    def __init__(self, verbose=True):
        super().__init__(base_url=UCL_BASE_URL, Uni_ID="UCL", Uni_name="University College London", verbose=verbose)

    # Override any method if UCL's site has a different structure or logic
    def _parse_programs(self, soup, _):
        program_url_pairs = {}

        for link in soup.find_all('a', href=True):
            link_url = link.get('href')
            link_name = link.get_text().strip().lower()

            # Check if the URL starts with the base URL
            if link_url.startswith(self.base_url):
                # Try to find the faculty info immediately following the link
                faculty_info = link.find_next_sibling(
                    "span", class_="search-results__dept")
                if faculty_info:
                    program_faculty = faculty_info.get_text().strip()
                else:
                    program_faculty = "N/A"  # Default value in case the faculty info is missing

                program_url_pairs[link_name] = [link_url, program_faculty]

        return program_url_pairs


class UCLProgramDetailsCrawler(BaseProgramDetailsCrawler):
    def __init__(self, test=False, verbose=True):
        super().__init__(Uni_ID="UCL", test=test, verbose=verbose)

    def process_row(self, row):
        link_bank = self.read_excel('data/url_bank.xlsx').active
        program_name, url, faculty = row

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        intro_div = soup.find('div', id='introduction')
        paragraphs = intro_div.find_all('p')
        if len(paragraphs) < 2:
            # When detail is not available: The details for this degree are being confirmed and will be published shortly.
            intro_text = paragraphs[0].text
        else:
            intro_text = paragraphs[1].text

        useful_links = []
        for link in soup.find_all('a'):
            link_name = link.get_text().strip()
            link_url = link.get('href')

            for bank_row in link_bank.iter_rows(min_row=2, values_only=True):
                if bank_row[0].lower() in link_name.lower():
                    useful_links.append(f'{link_name}:{link_url}')
                    break
        return [program_name, url, faculty, intro_text] + useful_links

    # Override any method if UCL's site has a different structure or logic
    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        # 使用正则来匹配可能的日期格式
        date_pattern = re.compile(
            r'(\b(January|February|March|April|May|June|July|August|September|October|November|December)\b \d{4})')

        # 寻找所有的div，其class属性为"prog-key-info__text"
        date_containers = soup.find_all('div', class_="prog-key-info__text")

        start_terms = []

        for container in date_containers:
            potential_date = date_pattern.search(container.text)
            if potential_date:
                surrounding_text = container.h5.text if container.h5 else ""
                # 使用关键词来确认这个日期是否与入学日期相关
                if any(term in surrounding_text.lower() for term in ['start', 'begin', 'commence']):
                    start_terms.append(potential_date.group())

        # 将找到的日期按序号加入到program_details字典中
        for idx, term in enumerate(start_terms, 1):
            key = f"入学月{idx}"
            program_details[key] = term

        if len(start_terms) == 0:
            program_details[f"入学月{1}"] = "未找到"

    def get_backgroud_requirements(self, soup, program_details, extra_data=None):
        # 定位标题为“Entry requirements”的<h2>标签
        h2_tag = soup.find('h2', string='Entry requirements')

        if not h2_tag:
            # 如果没有找到对应的标签，直接返回
            return

        # 获取<h2>标签之后的所有<p>标签的文本内容
        requirements = []
        for sibling in h2_tag.find_next_siblings():
            # 如果遇到其他的<h2>标签，则停止提取
            if sibling.name and sibling.name.startswith('h2'):
                break
            # 如果是<p>标签，则获取其文本内容
            if sibling.name == 'p':
                requirements.append(sibling.get_text(strip=True))

        # 将所有的<p>标签的文本内容合并成一个字符串，并保存到program_details字典中
        program_details[header.background_requirements] = ' '.join(
            requirements)

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        courses = []

        # 先捕获必修课程列表
        compulsory_modules_div = soup.find(
            'div', class_='prog-modules-mandatory')
        if compulsory_modules_div:
            for a_tag in compulsory_modules_div.find_all('a'):
                courses.append(a_tag.get_text(strip=True))
            for div_tag in compulsory_modules_div.find_all('div'):
                # 仅添加不包含<a>标签的<div>标签内容
                if not div_tag.find('a'):
                    courses.append(div_tag.get_text(strip=True))

        # 接下来捕获选修课程列表
        optional_modules_div = soup.find('div', class_='prog-modules-optional')
        if optional_modules_div:
            for a_tag in optional_modules_div.find_all('a'):
                courses.append(a_tag.get_text(strip=True))
            for div_tag in optional_modules_div.find_all('div'):
                # 仅添加不包含<a>标签的<div>标签内容
                if not div_tag.find('a'):
                    courses.append(div_tag.get_text(strip=True))

        # 将捕获的课程列表添加到program_details字典中
        program_details[header.course_list_english] = '\n'.join(courses)
        if len(courses) == 0:
            program_details[header.course_list_english] = "未找到"

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

        entry_req_tag = soup.find(id="entry-requirements")
        if entry_req_tag:
            entry_req_paragraph = entry_req_tag.find(
                'h2').find_next_sibling('p')
            if entry_req_paragraph:
                text = entry_req_paragraph.get_text().lower()
                combined_text = self.extract_relevant_text(text, phrases)
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
        entry_req_tag = soup.find(id="entry-requirements")
        if entry_req_tag:
            entry_req_paragraph = entry_req_tag.find(
                'h2').find_next_sibling('p')
            if entry_req_paragraph:
                text = entry_req_paragraph.get_text().lower()
                combined_text = self.extract_relevant_text(text, phrases)
                if combined_text:
                    program_details[header.portfolio] = self.judge_portfolio_preference(
                        combined_text)
                    program_details[header.portfolio_details] = combined_text
                else:
                    program_details[header.portfolio] = "未要求"
        else:
            program_details[header.portfolio] = "未找到Entry requirements标签"

    def get_tuition(self, soup, program_details, extra_data=None):
        # 查找包含"Overseas tuition fees"的<h5>标签
        tuition_tag = soup.find(
            'h5', string=lambda text: 'Overseas tuition fees' in text)
        if tuition_tag:
            # 从该标签开始，查找具有class属性值为"study-mode fulltime"的<div>标签
            fulltime_fee_div = tuition_tag.find_next(
                'div', {'class': 'study-mode fulltime'})
            parttime_fee_div = tuition_tag.find_next(
                'div', {'class': 'study-mode parttime'})
            if fulltime_fee_div:
                # 提取文本内容并去除多余的空白字符
                tuition_fee = fulltime_fee_div.get_text(
                    strip=True).replace('&#163;', '£')
                program_details[header.course_fee] = tuition_fee
            elif parttime_fee_div:
                # 提取文本内容并去除多余的空白字符
                tuition_fee = parttime_fee_div.get_text(
                    strip=True).replace('&#163;', '£')
                program_details[header.course_fee] = tuition_fee + \
                    " (part-time)"
            else:
                program_details[header.course_fee] = "未找到"
        else:
            program_details[header.course_fee] = "未找到"

    def get_period(self, soup, program_details, extra_data=None):
        period_tag = soup.find('h5', string=lambda text: 'Duration' in text)
        if period_tag:
            headers = [header.course_duration_1, "课程时长2(学制)", "课程时长3(学制)"]
            index = 0

            # 从该标签开始，查找具有class属性值为"study-mode ...time"的<div>标签
            fulltime_div = period_tag.find_next(
                'div', {'class': 'study-mode fulltime'})
            parttime_div = period_tag.find_next(
                'div', {'class': 'study-mode parttime'})
            flexible_div = period_tag.find_next(
                'div', {'class': 'study-mode flexible'})

            # 提取文本内容并去除多余的空白字符
            if fulltime_div:
                fulltime_period = fulltime_div.get_text(
                    strip=True)
                if fulltime_period != "Not applicable":
                    program_details[headers[index]] = fulltime_period + \
                        " (full-time)"
                    index += 1
            if parttime_div:
                parttime_period = parttime_div.get_text(
                    strip=True)
                if parttime_period != "Not applicable":
                    program_details[headers[index]] = parttime_period + \
                        " (part-time)"
                    index += 1
            if flexible_div:
                flexible_period = flexible_div.get_text(
                    strip=True)
                if flexible_period != "Not applicable":
                    program_details[headers[index]] = flexible_period + \
                        " (flexible)"
                    index += 1

            if index == 0:
                program_details[header.course_duration_1] = "未找到"

    def get_language_requirements(self, soup, program_details, extra_data=None):
        # 定义雅思得分级别的字典
        ielts_scores = {
            "Level 1": ("总分 6.5, 小分 6.0", "Level 1: Overall score of 6.5 and a minimum of 6.0 in each component"),
            "Level 2": ("总分 7.0, 小分 6.5", "Level 2: Overall score of 7.0 and a minimum of 6.5 in each component"),
            "Level 3": ("总分 7.0, 小分 7.0", "Level 3: Overall score of 7.0 and a minimum of 7.0 in each component"),
            "Level 4": ("总分 7.5, 小分 7.0", "Level 4: Overall score of 7.5 and a minimum of 7.0 in each component"),
            "Level 5": ("总分 8.0, 小分 8.0", "Level 5: Overall score of 8.0 and a minimum of 8.0 in each component")
        }

        # 在全文的<p>标签中搜索包含"Level N"的文本
        for i in range(1, 6):
            level_text = f"Level {i}"
            matching_paragraph = soup.find(
                string=lambda text: level_text in text)

            if matching_paragraph:
                program_details[header.ielts_requirement] = ielts_scores[level_text][0]
                program_details[header.ielts_remark] = ielts_scores[level_text][1]
                return  # 找到一个匹配后即退出循环，确保只有一个级别的数据被添加到字典中
        program_details[header.ielts_requirement] = "未找到"
        program_details[header.ielts_remark] = "未找到"

    def get_GRE_GMAT_requirements(self, soup, program_details, extra_data=None):
        gre_texts = []
        gmat_texts = []

        # 正则表达式确保GRE和GMAT前后有空白或标点
        gre_pattern = re.compile(r'\bGRE\b', re.IGNORECASE)
        gmat_pattern = re.compile(r'\bGMAT\b', re.IGNORECASE)

        for p in soup.find_all('p'):
            if gre_pattern.search(p.get_text()):
                gre_texts.append(p.get_text().strip())
            if gmat_pattern.search(p.get_text()):
                gmat_texts.append(p.get_text().strip())

        # 如果找到GRE或GMAT相关的文本，将它们合并并添加到program_details
        if gre_texts:
            program_details[header.gre] = ' '.join(gre_texts)
        else:
            program_details[header.gre] = "未要求"
        if gmat_texts:
            program_details[header.gmat] = ' '.join(gmat_texts)
        else:
            program_details[header.gmat] = "未要求"

    def get_major_requirements_for_chinese_students(self, soup, program_details, extra_data=None):

        # 请求的URL
        url = "https://www.ucl.ac.uk/prospective-students/graduate/system/ajax"

        # # 请求表单页面
        # url_form = program_url
        # response = requests.get(url_form)
        #
        # # 使用 BeautifulSoup 解析页面
        # soup_form = BeautifulSoup(response.text, 'html.parser')

        # 提取 form_build_id
        form_build_id = soup.find('input', {'name': 'form_build_id'})['value']

        # 设置请求头信息
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.ucl.ac.uk",
            "Referer": "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/health-wellbeing-and-sustainable-buildings-msc",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "macOS",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        # 如果POST请求需要数据，您需要在下面的数据字典中添加
        data = {
            'ucl_international_equivalencies': 'CN',
            'form_build_id': form_build_id,
            'form_id': 'ucl_programmes_international_equivalencies_form',
            '_triggering_element_name': 'ucl_international_equivalencies'
        }

        # try:
        #     response = requests.post(url, headers=headers, data=data)
        # except requests.ConnectionError as e:
        #     print(f"ConnectionError for URL {url}: {e}")
        #
        time.sleep(0.2)
        response = request_with_retry(
            url=url,
            method='POST',
            headers=headers,
            data=data,
            Uni_ID="UCL",
            max_retries=10,
            delay=10
        )

        # response = requests.post(url, headers=headers, data=data)

        json_data = {}
        try:
            json_data = response.json()
        except:
            program_details[header.local_student_requirements] = "未找到，项目页面不可用或者正在更新"

        all_text = ""

        # 遍历 JSON 数据，查找 "command": "insert" 的项
        for item in json_data:
            if item.get('command') == 'insert':
                # 使用 BeautifulSoup 提取 data 中的 <p> 标签内容
                soup = BeautifulSoup(item['data'], 'html.parser')
                p_tags = soup.find_all('p')
                for p in p_tags:
                    all_text += p.text + ' '

        # 使用正则表达式匹配文本中的百分比
        match = re.search(r'(\d{2})%', all_text)

        if match:
            percentage = int(match.group(1))
            if percentage == 80:
                program_details[header.local_student_requirements] = "2:2"
            elif percentage == 85:
                program_details[header.local_student_requirements] = "2:1"
            else:
                program_details[header.local_student_requirements] = str(
                    percentage) + '%'
            return
        else:
            # Find the h4 element with the text 'Equivalent qualifications for China'
            h4_tag = soup.find(
                'h4', text='Equivalent qualifications for China')

            if h4_tag:
                # Find the next sibling <p> element after the h4 tag
                program_details[header.local_student_requirements] = h4_tag.find_next_sibling(
                    'p').get_text()
            else:
                program_details[header.local_student_requirements] = "未找到"

    def is_conditional_upper_second(self, text):
        phrases_pt1 = ["with a lower than upper-second class",
                       "normally require an upper second-class",
                       "with a lower second",
                       "upper second-class"]

        phrases_pt2 = [
            "second acceptable qualification",
            "equivalent overseas qualification",
            "in exceptional cases",
            "in exceptional circumstances",
            "fail to meet the standard requirement",
            "may, at their discretion, consider",
            "may also be considered",
            "may be considered",
            "may also be accepted",
            "may be accepted",
            "may be admitted"]

        return any(phrase in text for phrase in phrases_pt1) and any(phrase in text for phrase in phrases_pt2)

    def is_upper_second_class(self, text):
        upper_2nd_phrases = ["upper second-class",
                             "upper second class",
                             "upper-second class",
                             "1st class",
                             "a good 2.1",
                             "a first-class",
                             "a first class",
                             "2:1 or equivalent",
                             "dental qualification"
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
        entry_req_tag = soup.find(id="entry-requirements")
        if entry_req_tag:
            entry_req_paragraph = entry_req_tag.find(
                'h2').find_next_sibling('p')
            if entry_req_paragraph:
                text = entry_req_paragraph.get_text().lower()
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

        # 搜索包含这些关键词的<p>标签
        entry_req_tag = soup.find(id="entry-requirements")
        combined_text = ""
        if entry_req_tag:
            entry_req_paragraph = entry_req_tag.find(
                'h2').find_next_sibling('p')
            if entry_req_paragraph:
                text = entry_req_paragraph.get_text().lower()
                combined_text = self.extract_relevant_text(text, keywords)

        # 将合并后的文本添加到program_details字典中
        if combined_text:
            program_details[header.exam_requirements] = self.judge_interview_preference(
                combined_text)
            program_details[header.exam_requirements_details] = combined_text
        else:
            program_details[header.exam_requirements] = "未要求"

    def get_major_specifications(self, soup, program_details, extra_data=None):
        # Todo: 写爬虫更新而不是直接复制粘贴
        # Load the excel worksheet
        worksheet = self.read_excel(
            "data/UCL/program_specifications.xlsx").active

        # Extract program URL from program_details
        program_url = program_details.get(header.website_link, "")

        # Start from the second row to skip header
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            sheet_url = row[0]

            if program_url == sheet_url:
                # Add the specifications to program_details
                for i in range(1, 15):  # assuming you have up to 14 specializations
                    if row[i]:  # Check if the specialization is not None
                        column_name = f"专业细分方向{i}"
                        program_details[column_name] = row[i]

                break  # Break the loop once the URL is found

        return program_details
