from spiders import UCL
from spiders import ED


def UCL_caller():
    print("crawling program details...")
    ucl_program_crawler = UCL.UCLProgramURLCrawler()
    ucl_program_crawler.crawl()
    print("crawling UCL details...")
    ucl_detail_crawler = UCL.UCLProgramDetailsCrawler(test=False, verbose=False)
    # ucl_detail_crawler.get_program_useful_links()
    ucl_detail_crawler.generate_program_details(translate=True)


def ED_caller():
    print("crawling program details...")
    # program_crawler = ED.EDProgramURLCrawler()
    # program_crawler.crawl()
    print("crawling UCL details...")
    detail_crawler = ED.EDProgramDetailsCrawler(test=False, verbose=True)
    # detail_crawler.get_program_useful_links()
    detail_crawler.generate_program_details(translate=False)

def main():
    ED_caller()




if __name__ == "__main__":
    main()
