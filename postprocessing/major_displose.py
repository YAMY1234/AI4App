import pandas as pd
import re
from config.program_details_header import header


def filter_programs(school_abbr):
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
