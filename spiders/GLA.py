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

    # Todo: add all rewrite logic here
