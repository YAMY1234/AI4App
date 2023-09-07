from spiders import UCL
from spiders import ED


def UCL_caller():
    ucl_program_crawler = UCL.UCLProgramURLCrawler(verbose=True)
    ucl_program_crawler.crawl()
    ucl_detail_crawler = UCL.UCLProgramDetailsCrawler(test=False, verbose=False)
    # ucl_detail_crawler.get_program_useful_links()
    ucl_detail_crawler.generate_program_details(translate=True)


def ED_caller():
    program_crawler = ED.EDProgramURLCrawler(verbose=True)
    program_crawler.crawl()
    detail_crawler = ED.EDProgramDetailsCrawler(test=False, verbose=True)
    # detail_crawler.get_program_useful_links()
    detail_crawler.generate_program_details(translate=False)

def main():
    ED_caller()




if __name__ == "__main__":
    main()
