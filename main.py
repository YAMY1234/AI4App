from spiders import UCL



def main():
    print("crawling program details...")
    ucl_program_crawler = UCL.UCLProgramURLCrawler()
    ucl_program_crawler.crawl()
    print("crawling UCL details...")
    ucl_detail_crawler = UCL.UCLProgramDetailsCrawler()
    # ucl_detail_crawler.get_program_useful_links()
    ucl_detail_crawler.scrape_program_details()
    # 具体实现...

if __name__ == "__main__":
    main()
