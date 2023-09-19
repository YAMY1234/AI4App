from spiders import UCL
from spiders import ED
from postprocessing import replace_constant
from config.program_details_header import header


def UCL_caller():
    ucl_program_crawler = UCL.UCLProgramURLCrawler(verbose=True)
    ucl_program_crawler.crawl()
    ucl_detail_crawler = UCL.UCLProgramDetailsCrawler(test=False, verbose=False)
    # ucl_detail_crawler.get_program_useful_links()
    ucl_detail_crawler.generate_program_details(translate=True)


def ED_caller():
    program_crawler = ED.EDProgramURLCrawler(verbose=True)
    program_crawler.crawl()
    detail_crawler = ED.EDProgramDetailsCrawler(test=False, verbose=False)
    detail_crawler.get_program_useful_links()
    detail_crawler.generate_program_details(translate=False)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.college)


def main():
    ED_caller()


if __name__ == "__main__":
    main()
