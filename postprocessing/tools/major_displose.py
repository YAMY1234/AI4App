import pandas as pd
import re
from config.program_details_header import header

degrees = ["MSc", "MA", "MBA", "MPhil", "LLM", "MFA", "MMus", "MEd", "MEng", "MPH", "MSW",
           "MCouns", "PHD", "MScR", "Mth", "MArch", 'MClinDent', "MPA", "MPlan", "MASc", "MLA"]

unwanted_degrees = ["MRes", "grad dip", "pg cert", "pg dip", "Distance learning programme"]

conjunctions = ["and", "but", "or", "nor", "for", "so", "yet"]

prepositions = ["about", "above", "across", "after", "against", "along", "amid", "among", "around", "as",
                "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by",
                "concerning", "considering", "despite", "down", "during", "except", "for", "from", "in",
                "inside", "into", "like", "near", "of", "on", "onto", "out", "outside", "over", "past",
                "regarding", "round", "since", "through", "to", "toward", "under", "underneath", "until",
                "unto", "up", "upon", "with", "within", "without"]


'''
第一种情况，判断是否有括号：
    如果有括号，那么判断括号里面的内容有没有专业名
        如果有专业名，那么去掉括号，把整个括号里面的内容提到句子的最前端，否则保持原样
        将所有单词转换为首字母大写，
        用空格分割每一个单词，
        如果单词的小写形式在 prepositions 或者 conjunctions 当中出现，那么保持不变，否则将单词首字母大写
        如果单词的小写形式在 degrees 或者 unwanted_degrees 的小写形式 当中出现，那么将这个单词放在句子的开头，同时首字母大写
        用空格将所有单词拼接成一个字符串
否则，第二种情况（没有括号）：
    用逗号分割字符串，
    对于每个字符串
        将所有单词转换为首字母大写，
        用空格分割每一个单词，
        如果单词的小写形式在 prepositions 或者 conjunctions 当中出现，那么保持不变，否则将单词首字母大写
        如果单词的小写形式在 degrees 或者 unwanted_degrees 的小写形式 当中出现，那么将这个单词放在句子的开头，同时首字母大写
        用空格将所有单词拼接成一个字符串
    通过字符串的长度重新排序
    用逗号拼接所有的字符串
'''
def rearrange_program_name(name):
    degrees_lower = {}
    for degree in degrees:
        degrees_lower[degree.lower()] = degree

    def handle_words(words):
        # Move degree words to the start and capitalize the first letter
        words = [w for w in words if w.lower() not in degrees_lower] + \
                [w for w in words if w.lower() in degrees_lower]

        # Capitalize words except prepositions, conjunctions and degrees
        words = [w.capitalize() if w.lower() not in prepositions + conjunctions else w for w in words]
        new_words = []
        for word in words:
            if word.lower() not in prepositions + conjunctions:
                word.capitalize()
            if word.lower() in degrees_lower:
                new_words.insert(0, degrees_lower[word.lower()])
            else:
                new_words.append(word)
        if '' in new_words:
            new_words.remove('')
        return ' '.join(new_words)

    if '(' in name and ')' in name:
        content_inside_parentheses = re.findall(r'\((.*?)\)', name)[0]
        remaining_name = re.sub(r'\(.*?\)', '', name).strip()

        if any(degree.lower() in content_inside_parentheses.lower() for degree in degrees):
            words = (content_inside_parentheses + ' ' + remaining_name)
            words = re.split("[,\s]", words)
        else:
            if ',' in name:
                return "无法处理该专业：" + name
            words = re.split("[,\s]", name)

        rearranged_name = handle_words(words)

    else:
        segments = name.split(',')
        segments = [handle_words(segment.split()) for segment in segments]
        segments.sort(key=len)
        rearranged_name = ', '.join(segments)

    return rearranged_name


'''
输入参数：
    program_detail_path: str
    col_name1: str
    col_name2: str
    transfer_words_list: list
函数功能：
    1. 读取program_detail_path的excel
    2. 对于col_name1，如果cell当中包含transfer_words_list当中的某一个词(比如A)，
    那么就删除col_name1当中对应匹配到的那个词，同时在col_name2对应的cell的文本后面加入这个词
    3. 保存更新后的数据到原文件
'''
def transfer_words(program_detail_path, col_name1, col_name2, transfer_words_list):
    # 读取Excel文件
    df = pd.read_excel(program_detail_path, engine='openpyxl')

    # 对于指定列，删除特定的文本，并插入新词
    for index in range(len(df)):
        cell_value1 = df.at[index, col_name1]
        cell_value2 = df.at[index, col_name2]
        for word in transfer_words_list:
            pattern = re.compile(word)
            # 如果cell当中包含这个word
            if pattern.search(str(cell_value1)):
                # 删除cell当中的这个word
                cell_value1 = pattern.sub('', str(cell_value1))
                # 在cell2当中加入这个word
                cell_value2 = str(cell_value2) + " " + word

    # 将更改后的数据帧保存回Excel文件
    df.to_excel(program_detail_path, index=False, engine='openpyxl')

'''
函数参数：
    一个string，里面可能有很多内容，包括日期
函数功能：
    1. 将这个string当中提取所有的日期，然后将这些日期转换为"YYYY-MM-DD"的格式
    （注意，提取的时候需要考虑所有的格式（英文的），比如"Jan 2021"，"January 2021"，"2021 Jan"，"2021 January"）
    将日期的list通过换行拼接
    返回对应的结果
'''
def rearrange_date(date):
    # 定义所有日期的pattern
    patterns_numeral = [
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
        r'\d{4}[-/]\d{1,2}',
        r'\d{1,2}[-/]\d{4}',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{1,2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}',
        r'\d{4}[-/]\d{1,2} \d{1,2}:\d{1,2}',
        r'\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4}[-/]\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{4}[-/]\d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{1,2}[-/]\d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
    ]
    patterns_with_month_abbr = [
        r'\w{3} \d{4}',
        r'\w{3} \d{1,2} \d{4}',
        r'\d{4} \w{3}',
        r'\d{4} \w{3} \d{1,2}',
        r'\w{3} \d{4} \d{1,2}:\d{1,2}',
        r'\w{3} \d{1,2} \d{4} \d{1,2}:\d{1,2}',
        r'\d{4} \w{3} \d{1,2}:\d{1,2}',
        r'\d{4} \w{3} \d{1,2} \d{1,2}:\d{1,2}',
        r'\w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\w{3} \d{1,2} \d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4} \w{3} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\w{3} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\w{3} \d{1,2} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{4} \w{3} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{4} \w{3} \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
    ]
    patterns_with_month_full = [
        r'\w+ \d{4}',
        r'\w+ \d{1,2} \d{4}',
        r'\d{4} \w+',
        r'\d{4} \w+ \d{1,2}',
        r'\w+ \d{4} \d{1,2}:\d{1,2}',
        r'\w+ \d{1,2} \d{4} \d{1,2}:\d{1,2}',
        r'\d{4} \w+ \d{1,2}:\d{1,2}',
        r'\d{4} \w+ \d{1,2} \d{1,2}:\d{1,2}',
        r'\w+ \d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\w+ \d{1,2} \d{4} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4} \w+ \d{1,2}:\d{1,2}:\d{1,2}',
        r'\d{4} \w+ \d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
        r'\w+ \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\w+ \d{1,2} \d{4} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{4} \w+ \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
        r'\d{4} \w+ \d{1,2} \d{1,2}:\d{1,2}:\d{1,2} \w{2}',
    ]
    all_patterns = patterns_numeral + patterns_with_month_abbr + patterns_with_month_full
    # 用上面这些pattern来匹配日期
    match_group = [] # e.g. store all tuples like (matched_text, start_index, end_index)
    for pattern in all_patterns:
        match_group += re.findall(pattern, date)
    # find the smallest start_index and the corresponding date, erase the matched text in date
    while len(match_group) > 0:
        smallest_start_index = 1000
        smallest_start_index_index = 0
        for index, match in enumerate(match_group):
            if match[1] < smallest_start_index:
                smallest_start_index = match[1]
                smallest_start_index_index = index
        matched_text = match_group[smallest_start_index_index][0]
        date = date.replace(matched_text, match_group[smallest_start_index_index][0])
        match_group.pop(smallest_start_index_index)




def rearrange_name(school_abbr):
    program_details_path = f"data/{school_abbr}/program_details.xlsx"
    program_details_save_path = f"data/{school_abbr}/program_details_stage1.xlsx"

    df_program_details = pd.read_excel(program_details_path)

    # Iterate over the specified column and replace its content

    df_program_details[header.major] = df_program_details[header.major].apply(rearrange_program_name)

    # Save the modified DataFrame back to the Excel file
    df_program_details.to_excel(program_details_save_path, index=False)


def filter_programs(school_abbr):

    program_details_path = f"data/{school_abbr}/program_details_stage1.xlsx"

    # 读取数据
    df_program_details = pd.read_excel(program_details_path)

    # 修改匹配逻辑，使其不区分大小写
    mask_wanted_degree = df_program_details["专业"].apply(lambda x: any(keyword.lower() in x.lower() for keyword in degrees))
    mask_online = ~df_program_details["专业"].str.lower().str.contains("online")
    # mask_unwanted_degree = ~df_program_details["专业"].apply(lambda x: any(keyword in x.lower() for keyword in unwanted_degrees))

    # 组合两个masks
    combined_mask = mask_wanted_degree & mask_online

    df_filtered = df_program_details[combined_mask]

    # 保存更新后的数据到原文件
    df_filtered.to_excel(program_details_path, index=False)
