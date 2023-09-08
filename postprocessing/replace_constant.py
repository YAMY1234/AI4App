import pandas as pd
from config.program_details_header import header


def replace_from_standard(school_abbr, col_name):
    """
    Reads '官网链接' from standard_{school_abbr}.xlsx and compares with program_details.xlsx.
    If a match is found, updates the '学院' column in program_details.xlsx using data from standard_{school_abbr}.xlsx
    and then rewrites program_details.xlsx with the updated information.

    :param school_abbr: Abbreviation of the school name.
    :type school_abbr: str
    """

    # 路径定义
    standard_path = f"data/{school_abbr}/standard_{school_abbr}.xlsx"
    program_details_path = f"data/{school_abbr}/program_details.xlsx"

    # 读取文件
    df_standard = pd.read_excel(standard_path)
    df_program_details = pd.read_excel(program_details_path)

    # 使用字典存储“官网链接”与“学院”的映射关系
    link_to_college = dict(zip(df_standard[header.website_link], df_standard[col_name]))

    # 更新program_details的学院列
    df_program_details[col_name] = df_program_details[header.website_link].map(link_to_college).fillna(
        df_program_details[col_name])

    # 保存更新后的数据到原文件
    df_program_details.to_excel(program_details_path, index=False)

# replace_from_standard(school_abbr="ED", col_name=header.college)
