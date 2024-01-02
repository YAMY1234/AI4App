import re

import pandas as pd

from config.program_details_header import header
from postprocessing.tools import replace_constant
from postprocessing.tools.base_api import dispose_major_caller, replace_standard_caller, ask_gpt_caller, \
    translate_api_caller, replace_standard_external_caller
from postprocessing.tools.replace_constant import remove_specific_text

'''
1. 专业漏了一批MSc(MedSci)开头的专业和一个MAcc开头的专业，之后需要补上去
'''
school_abbr: str = "GLA"


def rearrange_name(school_abbr=school_abbr):
    def extract_and_move_name(name):
        # 使用正则表达式查找" [XXX]"的模式
        match = re.search(r'\[(.*?)\]', name)

        if match:
            # 提取匹配的内容
            extracted_text = match.group(1)

            # 将提取的内容移到name前面
            new_name = extracted_text + " " + name.replace(match.group(0), '')

            return new_name
        else:
            # 如果没有匹配到" [XXX]"的模式，直接返回原始name
            return name

    program_details_path = f"data/{school_abbr}/program_details.xlsx"

    df_program_details = pd.read_excel(program_details_path)

    # Iterate over the specified column and replace its content

    df_program_details[header.major] = df_program_details[header.major].apply(extract_and_move_name)

    # Save the modified DataFrame back to the Excel file
    df_program_details.to_excel(program_details_path, index=False)


def filter_programs(school_abbr=school_abbr):
    def extract_keywords(s):
        """提取关键词，并处理/或()的情况"""
        first_word = s.split()[0]

        if '/' in first_word:
            return first_word.split('/')

        elif '(' in first_word and ')' in first_word:
            inside_brackets = re.search(r'\((.*?)\)', first_word).group(1)
            return [first_word.replace(f"({inside_brackets})", "").strip(), inside_brackets]

        else:
            return [first_word]

    standard_path = f"data/{school_abbr}/standard_{school_abbr}.xlsx"
    program_details_path = f"data/{school_abbr}/program_details.xlsx"

    # 从standard文件中读取数据
    df_standard = pd.read_excel(standard_path)

    # 提取"专业"列的关键词，并将返回的列表展平
    extracted_keywords = df_standard["专业"].apply(extract_keywords).tolist()
    flattened_keywords = [item for sublist in extracted_keywords for item in sublist]

    # 去除重复项
    keywords = list(set(flattened_keywords))
    keywords.append("MSc(MedSci)")
    keywords.append("MAcc")
    print(keywords)

    # 从program_details文件中读取数据
    df_program_details = pd.read_excel(program_details_path)

    # 将关键词列表中的每个关键词都转为小写
    keywords = [keyword.lower() for keyword in keywords]

    # 修改匹配逻辑，使其不区分大小写
    mask_keyword = df_program_details["专业"].apply(lambda x: any(keyword in x.lower() for keyword in keywords))
    mask_online = ~df_program_details["专业"].str.lower().str.contains("online")

    # 组合两个masks
    combined_mask = mask_keyword & mask_online

    df_filtered = df_program_details[combined_mask]

    # 保存更新后的数据到原文件
    df_filtered.to_excel(program_details_path, index=False)



def external_dispose(school_abbr):
    external_replace_col_list = [
        header.application_deadlines,
        header.course_list_english,
        header.course_list_chinese,
        header.college_chinese,
        header.background_requirements_chinese,
        header.project_intro_chinese,
        header.major_chinese,
        header.school_chinese_name
    ]
    replace_standard_external_caller(school_abbr=school_abbr, col_name_list=external_replace_col_list, standard_path="/Users/liyangmin/Documents/创业/英硕项目/格拉斯哥- 工作经验修复.xlsx")



def remove_text_dispose(school_abbr):
    # col_name_list = [header.project_intro_chinese, header.project_intro]
    # remove_word_list = ["今天了解更多信息。", "了解.*?信息。", "Find out more about.*?\."]
    # remove_specific_text(school_abbr, col_name_list, remove_word_list)
    # 10.9 录取要求处理
    col_name_list = [header.background_requirements]
    remove_word_list = ["International students with academic qualifications below those required should contact our partner institution, Glasgow International College, who offer a range of pre-Masters courses."]
    remove_specific_text(school_abbr, col_name_list, remove_word_list)

def GLA_post_dispose():
    # STAGE2
    # dispose_major_caller(school_abbr=school_abbr, func_rearrange_name=rearrange_name, func_filter_programs=filter_programs)

    # replace_standard_caller(school_abbr=school_abbr)

    # external_dispose(school_abbr=school_abbr)

    remove_text_dispose(school_abbr=school_abbr)

    # STAGE3
    # gpt_col_list = [
    #     header.application_deadlines,
    #     header.course_list_english,
    # ]
    #
    # ask_gpt_caller(school_abbr=school_abbr, col_name_list=gpt_col_list)
    #
    # translate_col_tuple_list = [
    #     header.course_list_chinese,
    #     header.background_requirements_chinese,
    #     header.project_intro_chinese,
    # ]
    # translate_api_caller(school_abbr=school_abbr, col_name_tuple_list=translate_col_tuple_list)


GLA_post_dispose()