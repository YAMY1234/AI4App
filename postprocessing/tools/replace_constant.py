import os
import re

import pandas as pd
from config.program_details_header import header


def replace_from_standard(school_abbr, col_name, standard_path=None):
    """
    Reads '官网链接' from standard_{school_abbr}.xlsx and compares with program_details.xlsx.
    If a match is found, updates the '学院' column in program_details.xlsx using data from standard_{school_abbr}.xlsx
    and then rewrites program_details.xlsx with the updated information.

    :param school_abbr: Abbreviation of the school name.
    :type col_name: str
    """

    def get_base_url(url):
        """截取URL到倒数第二个'/'字符为止"""
        if school_abbr == "GLA":
            return "/".join(url.split("/")[:-1])
        else:
            return url

    # 路径定义
    if not standard_path:
        standard_path = f"data/{school_abbr}/standard_{school_abbr}.xlsx"
    program_details_path = f"data/{school_abbr}/program_details.xlsx"
    program_details_stage1_path = f"data/{school_abbr}/program_details_stage1.xlsx"
    if "program_details_stage1.xlsx" in os.listdir(f'data/{school_abbr}'):
        df_program_details = pd.read_excel(program_details_stage1_path)
    else:
        df_program_details = pd.read_excel(program_details_path)

    df_standard = pd.read_excel(standard_path)

    # 使用字典存储“官网链接”与“XXX”的映射关系，但在这里，我们需要确保链接都被处理成基础URL
    link_to_college = dict(zip(df_standard[header.website_link].apply(get_base_url), df_standard[col_name]))

    # df_program_details[col_name] = df_program_details[header.website_link].map(link_to_college).fillna(
    #     df_program_details[col_name])
    for index, row in df_program_details.iterrows():
        # 获取官网链接值并转换为基础URL
        website_link_value = get_base_url(row[header.website_link])

        # 检查这个值是否在link_to_college字典中
        if website_link_value in link_to_college:
            df_program_details.at[index, col_name] = link_to_college[website_link_value]

    # 保存更新后的数据到原文件
    df_program_details.to_excel(program_details_stage1_path, index=False)


def remove_specific_text(school_abbr, col_name_list, remove_word_list):
    file_path = f"data/{school_abbr}/program_details_stage1.xlsx"
    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')

    # 对于指定列，删除特定的文本
    for col_name in col_name_list:
        if col_name in df.columns:
            for index in range(len(df)):
                cell_value = df.at[index, col_name]
                for word in remove_word_list:
                    pattern = re.compile(word)
                    cell_value = pattern.sub('', str(cell_value))
                df.at[index, col_name] = cell_value

    # 将更改后的数据帧保存回Excel文件
    df.to_excel(file_path, index=False, engine='openpyxl')

def replace_specific_text(school_abbr, col_name_list, remove_word_list, replace_word_list):
    file_path = f"data/{school_abbr}/program_details_stage1.xlsx"
    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')

    # 确保remove_word_list和replace_word_list的长度相同
    if len(remove_word_list) != len(replace_word_list):
        raise ValueError(f"remove_word_list和replace_word_list的长度必须相同: len(remove_word_list) {len(remove_word_list)}, len(replace_word_list): {len(replace_word_list)}")

    # 对于指定列，删除特定的文本，并插入新词
    for col_name in col_name_list:
        if col_name in df.columns:
            for index in range(len(df)):
                cell_value = df.at[index, col_name]
                for word_to_remove, word_to_replace in zip(remove_word_list, replace_word_list):
                    pattern = re.compile(word_to_remove)
                    cell_value = pattern.sub(word_to_replace, str(cell_value))
                df.at[index, col_name] = cell_value

    # 将更改后的数据帧保存回Excel文件
    df.to_excel(file_path, index=False, engine='openpyxl')

def replace_unwanted_character_and_empty_line(text):
    if isinstance(text, str):
        if len(text) == 0:
            return ""
    else:
        print("ERROR, not a text type")
        return ""
    text = re.sub(r'\[\[\[.*?\]\]\]', '', text)
    data = text.split("\n")
    new_data = ""
    for line in data:
        if len(line) > 0 and (line[0].isalpha() or line[0].isdigit()):
            new_data += f"{line}\n"
    return new_data

def replace_unwanted(school_abbr, col_name, func=replace_unwanted_character_and_empty_line):
    # Load the Excel file into a DataFrame
    program_details_path = f"data/{school_abbr}/program_details.xlsx"
    program_details_gpt_path = f"data/{school_abbr}/program_details_gpt.xlsx"

    if "program_details_gpt.xlsx" in os.listdir(f'data/{school_abbr}'):
        df_program_details = pd.read_excel(program_details_gpt_path)
    else:
        df_program_details = pd.read_excel(program_details_path)

    df_program_details[col_name] = df_program_details[col_name].apply(func)

    # Save the modified DataFrame back to the Excel file
    df_program_details.to_excel(program_details_gpt_path, index=False)