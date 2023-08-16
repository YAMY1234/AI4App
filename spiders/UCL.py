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
