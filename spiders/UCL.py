import re

import requests
from bs4 import BeautifulSoup

from .base_spider import BaseProgramURLCrawler, BaseProgramDetailsCrawler

UCL_BASE_URL = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees"


class UCLProgramURLCrawler(BaseProgramURLCrawler):
    def __init__(self):
        super().__init__(base_url=UCL_BASE_URL, school_name="UCL")

    # Override any method if UCL's site has a different structure or logic
    def _parse_programs(self, soup, program_words):
        program_url_pairs = {}
        for link in soup.find_all('a'):
            link_name = link.get_text().strip().lower()
            link_url = link.get('href')
            if "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/" not in link_url:
                continue
            for word in program_words:
                if word in link_name:
                    program_url_pairs[link_name] = link_url
        return program_url_pairs


class UCLProgramDetailsCrawler(BaseProgramDetailsCrawler):
    def __init__(self):
        super().__init__(school_name="UCL")

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
        program_details["相关背景要求"] = ' '.join(requirements)

    def get_course_intro_and_details(self, soup, program_details, extra_data=None):
        courses = []

        # 先捕获必修课程列表
        compulsory_modules_div = soup.find('div', class_='prog-modules-mandatory')
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
        program_details["课程列表英"] = '\n'.join(courses)
        if len(courses) == 0:
            program_details[f"课程列表英"] = "未找到"

    def get_work_experience_requirements(self, soup, program_details, extra_data=None):
        entry_req_tag = soup.find('h2', text='Entry requirements')
        if entry_req_tag:
            for sibling in entry_req_tag.find_next_siblings():
                # 如果遇到另一个h2标签，跳出循环
                if sibling.name == 'h2':
                    break
                if sibling.name == 'p' and 'work experience' in sibling.get_text(strip=True).lower():
                    program_details["工作经验"] = sibling.get_text(strip=True)
                    return
        program_details[f"工作经验"] = "未要求"

    def get_portfolio_requirements(self, soup, program_details, extra_data=None):
        entry_req_tag = soup.find('h2', text='Entry requirements')
        if entry_req_tag:
            for sibling in entry_req_tag.find_next_siblings():
                # 如果遇到另一个h2标签，跳出循环
                if sibling.name == 'h2':
                    break
                if sibling.name == 'p' and 'portfolio' in sibling.get_text(strip=True).lower():
                    program_details["作品集"] = sibling.get_text(strip=True)
                    return
        program_details[f"作品集"] = "未要求"

    def get_tuition(self, soup, program_details, extra_data=None):
        # 查找包含"Overseas tuition fees"的<h5>标签
        tuition_tag = soup.find('h5', string=lambda text: 'Overseas tuition fees' in text)
        if tuition_tag:
            # 从该标签开始，查找具有class属性值为"study-mode fulltime"的<div>标签
            fulltime_fee_div = tuition_tag.find_next('div', {'class': 'study-mode fulltime'})
            parttime_fee_div = tuition_tag.find_next('div', {'class': 'study-mode parttime'})
            if fulltime_fee_div:
                # 提取文本内容并去除多余的空白字符
                tuition_fee = fulltime_fee_div.get_text(strip=True).replace('&#163;', '£')
                program_details["课程费用"] = tuition_fee
            elif parttime_fee_div:
                # 提取文本内容并去除多余的空白字符
                tuition_fee = parttime_fee_div.get_text(strip=True).replace('&#163;', '£')
                program_details["课程费用"] = tuition_fee
            else:
                program_details[f"课程费用"] = "未找到"
        else:
            program_details[f"课程费用"] = "未找到"

    def get_period(self, soup, program_details, extra_data=None):
        # 查找包含"Overseas tuition fees"的<h5>标签
        period_tag = soup.find('h5', string=lambda text: 'Duration' in text)
        if period_tag:
            # 从该标签开始，查找具有class属性值为"study-mode fulltime"的<div>标签
            fulltime_fee_div = period_tag.find_next('div', {'class': 'study-mode fulltime'})
            if fulltime_fee_div:
                # 提取文本内容并去除多余的空白字符
                study_period = fulltime_fee_div.get_text(strip=True).replace('&#163;', '£')
                program_details["课程时长1(学制）"] = study_period
            else:
                program_details[f"课程时长1(学制）"] = "未找到"
        else:
            program_details[f"课程时长1(学制）"] = "未找到"

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

    def get_language_requirements(self, soup, program_details, extra_data=None):
        # 定义雅思得分级别的字典
        ielts_scores = {
            "Level 1": ("6.5", "Level 1: Overall score of 6.5 and a minimum of 6.0 in each component"),
            "Level 2": ("7.0", "Level 2: Overall score of 7.0 and a minimum of 6.5 in each component"),
            "Level 3": ("7.0", "Level 3: Overall score of 7.0 and a minimum of 7.0 in each component"),
            "Level 4": ("7.5", "Level 4: Overall score of 7.5 and a minimum of 7.0 in each component"),
            "Level 5": ("8.0", "Level 5: Overall score of 8.0 and a minimum of 8.0 in each component")
        }

        # 在全文的<p>标签中搜索包含"Level N"的文本
        for i in range(1, 6):
            level_text = f"Level {i}"
            matching_paragraph = soup.find(string=lambda text: level_text in text)

            if matching_paragraph:
                program_details["雅思要求"] = ielts_scores[level_text][0]
                program_details["雅思备注"] = ielts_scores[level_text][1]
                return  # 找到一个匹配后即退出循环，确保只有一个级别的数据被添加到字典中
        program_details["雅思要求"] = "未找到"
        program_details["雅思备注"] = "未找到"

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
            program_details["GRE"] = ' '.join(gre_texts)
        else:
            program_details["GRE"] = "未要求"
        if gmat_texts:
            program_details["GMAT"] = ' '.join(gmat_texts)
        else:
            program_details["GMAT"] = "未要求"

    def get_major_requirements_for_local_students(self, soup, program_details, extra_data=None):

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

        try:
            response = requests.post(url, headers=headers, data=data)
        except requests.ConnectionError as e:
            print(f"ConnectionError for URL {url}: {e}")
            return
        # response = requests.post(url, headers=headers, data=data)
        print(f"response.status_code: {response.status_code}")
        try:
            json_data = response.json()
        except:
            program_details["该专业对本地学生要求"] = "未找到，json load error"
            return

        # print(json_data)

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
                program_details["该专业对本地学生要求"] = "2:2"
            elif percentage == 85:
                program_details["该专业对本地学生要求"] = "2:1"
            else:
                program_details["该专业对本地学生要求"] = "其他"
            return
        program_details["该专业对本地学生要求"] = "未找到，百分比错误"
