from openpyxl import load_workbook, Workbook
from bs4 import BeautifulSoup
from spiders import UCL
from tools.regex_parser import extract_gpa
# ...其他需要的导入...



def main():
    print("crawling program details...")
    ucl_program_crawler = UCL.UCLProgramURLCrawler()
    ucl_program_crawler.crawl()
    print("crawling UCL details...")
    ucl_detail_crawler = UCL.UCLProgramDetailsCrawler()
    ucl_detail_crawler.get_program_useful_links()
    # ucl_detail_crawler.scrape_program_details()
    # 具体实现...

if __name__ == "__main__":
    main()
