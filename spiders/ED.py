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
        # Locate the "Programme structure" panel
        panel_title = soup.find("h2", class_="panel-title", string="Programme structure")
        if not panel_title:
            program_details["课程列表英"] = "N/A"
            return

        # Navigate to the panel content div
        panel_body = panel_title.find_next_sibling("div", class_="panel-collapse").find("div", class_="panel-body")
        if not panel_body:
            program_details["课程列表英"] = "N/A"
            return

        # Extract all <li> tags without <a> tags within the panel content
        course_list = []
        for li in panel_body.find_all("li"):
            if not li.find("a"):  # Check if the <li> tag does not contain an <a> tag
                course_list.append(li.get_text(strip=True))

        # Join the course list to form a single string
        program_details["课程列表英"] = '; '.join(course_list)

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
        # Find the "Applying" h2 tag
        applying_h2 = soup.find("h2", string="Applying")

        if not applying_h2:
            program_details["课程时长1(学制)"] = "N/A"
            return

        # Navigate to the <div class="col-xs-12"> container
        col_div = applying_h2.find_next_sibling("div", class_="row").find("div", class_="col-xs-12")

        if not col_div:
            program_details["课程时长1(学制)"] = "N/A"
            return

        # Extract and search for duration info from text
        col_text = col_div.get_text(strip=True).lower()
        if "1 year full-time" in col_text:
            program_details["课程时长1(学制)"] = "1 year full-time"
        elif "2 years full-time" in col_text:
            program_details["课程时长1(学制)"] = "2 years full-time"
        else:
            # Handle more complex cases like: Awards: MSc (12-12 mth FT, 24-24 mth PT)
            import re
            match = re.search(r"\((\d+-\d+ mth FT)", col_text)
            if match:
                program_details["课程时长1(学制)"] = match.group(1)
            else:
                program_details["课程时长1(学制)"] = "N/A"

    def get_enrollment_deadlines(self, soup, program_details, extra_data=None):
        program_details["入学月1"] = "9"

    def get_tuition(self, soup, program_details, extra_data=None):
        h2_tag = soup.find('h2', text='Fees and costs')
        if not h2_tag:
            program_details[f"课程费用"] = "该项目未显示"
            return

        h3_tag = h2_tag.find_next('h3', text='Tuition fees')
        if not h3_tag:
            program_details[f"课程费用"] = "该项目未显示"
            return

        link_tag = h3_tag.find_next('a', href=True)
        if not link_tag:
            program_details[f"课程费用"] = "该项目未显示"
            return

        url = link_tag['href']

        # Sending POST request (assuming you meant POST, as you mentioned in your requirements)
        response = requests.get(url)
        if response.status_code != 200:
            program_details[f"课程费用"] = "该项目未显示"
            return

        response_soup = BeautifulSoup(response.text, 'html.parser')
        table = response_soup.find('table', {'class': 'table table-bordered'})
        if not table:
            program_details[f"课程费用"] = "该项目未显示"
            return

        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if columns and '2024/5' in columns[0].get_text():
                international_fee = columns[2].get_text().strip()
                program_details[f"课程费用"] = international_fee.replace("£", "").replace(",", "").split('.')[0]
                return

        program_details[f"课程费用"] = "该项目未显示"

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