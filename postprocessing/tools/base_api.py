import re

import pandas as pd

from config.program_details_header import header
from postprocessing.tools import replace_constant
from postprocessing.tools.ask_chatgpt import replace_from_GPT
from postprocessing.tools.ask_google_translate import ask_api_to_translate
from postprocessing.tools.major_displose import filter_programs, rearrange_name

'''
STAGE 1:
'''
def dispose_major_caller(school_abbr, func_rearrange_name=None, func_filter_programs=None):
    if not func_rearrange_name:
        func_rearrange_name = rearrange_name
    if not func_filter_programs:
        func_filter_programs = filter_programs
    func_rearrange_name(school_abbr=school_abbr)
    func_filter_programs(school_abbr=school_abbr)

def batch_replace_constant(school_abbr, col_name_list, standard_path=None):
    for col_name in col_name_list:
        replace_constant.replace_from_standard(school_abbr=school_abbr, col_name=col_name, standard_path=standard_path)

def replace_standard_caller(school_abbr):
    col_name_list = [
        header.college, header.college_chinese, header.major, header.major_id, header.major_chinese,
        header.school_chinese_name, header.major_specialization_1, header.major_specialization_2,
        header.major_specialization_3,
        header.major_specialization_4,
        header.major_specialization_5,
        header.major_specialization_6,
        header.major_specialization_7,
        header.major_specialization_8,
        header.major_specialization_9,
        header.major_specialization_10,
        header.major_specialization_11,
        header.major_specialization_12,
        header.major_specialization_13,
        header.major_specialization_14
    ]
    batch_replace_constant(school_abbr=school_abbr, col_name_list=col_name_list)

def replace_standard_external_caller(school_abbr, col_name_list, standard_path):
    batch_replace_constant(school_abbr, col_name_list, standard_path)

'''
STAGE 2:
'''

def ask_gpt_caller(school_abbr, col_name_list):
    for col_name in col_name_list:
        replace_from_GPT(school_abbr=school_abbr, col_name=col_name)

def translate_api_caller(school_abbr, col_name_tuple_list):
    for pair in col_name_tuple_list:
        ask_api_to_translate(school_abbr=school_abbr, col_name=pair[0], translated_col_name=pair[1])



