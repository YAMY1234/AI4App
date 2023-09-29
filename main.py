from postprocessing.ask_chatgpt import replace_from_GPT
from spiders import UCL, GLA
from spiders import ED
from postprocessing import replace_constant, major_displose
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

    major_displose.filter_programs(school_abbr="ED")

    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.college)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.college_chinese)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_id)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_chinese)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.school_chinese_name)

    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_1)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_2)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_3)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_4)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_5)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_6)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_7)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_8)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_9)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_10)
    replace_constant.replace_from_standard(school_abbr="ED", col_name=header.major_specialization_11)

    replace_from_GPT(school_abbr="ED", col_name=header.application_deadlines)


def GLA_caller():
    # program_crawler = GLA.GLAProgramURLCrawler(verbose=True)
    # program_crawler.crawl()

    # detail_crawler = GLA.GLAProgramDetailsCrawler(test=False, verbose=False)
    # detail_crawler.get_program_useful_links()
    # detail_crawler.generate_program_details(translate=False)
    #
    # major_displose.filter_programs(school_abbr="GLA")
    #
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.college)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.college_chinese)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_id)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_chinese)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.school_chinese_name)
    #
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_1)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_2)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_3)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_4)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_5)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_6)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_7)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_8)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_9)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_10)
    # replace_constant.replace_from_standard(school_abbr="GLA", col_name=header.major_specialization_11)

    replace_from_GPT(school_abbr="GLA", col_name=header.application_deadlines)


def main():
    # ED_caller()
    GLA_caller()


if __name__ == "__main__":
    main()
