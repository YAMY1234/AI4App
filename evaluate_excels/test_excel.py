'''
功能：比对excel表格中的数据
作者：袁新航
时间：2023-08-30
参数：1.两个文件的路径
2.要比对的列名字
'''

import argparse
import pandas as pd
from config.program_details_header import header


def main():
    # parser = argparse.ArgumentParser(description="比对excel表格中的数据")
    # parser.add_argument("standard_path", help="标准数据文件路径", default="C:\Users\Lenovo\Desktop\test_data\data1.xlsx", nargs='?')
    # parser.add_argument("ourdata_path", help="待比对数据文件路径", default="C:\Users\Lenovo\Desktop\test_data\data2.xlsx", nargs='?')
    # parser.add_argument("column_type", help="列名类型（'general' 或 'simple'）", default='simple', nargs='?')
    # args = parser.parse_args()
    standard_path = "C:/Users/Lenovo/Desktop/test_data/data1.xlsx"  # 人工爬的数据
    ourdata_path = "C:/Users/Lenovo/Desktop/test_data/data2.xlsx"  # 机器爬的数据
    column_type = "simple"  # general是总表，全部比对，simple是方便大家检查的表，只比对了一部分
    # general_names = ["专业ID","地区","学校英文名","学校中文名","QS排名2023","QS排名2022","学院",\
    #             "学院中文","专业","专业中文","相关背景要求","相关背景要求中","课程简介中","课程列表中",\
    #             "课程列表英","官网链接","课程时长1（学制）1","课程时长1（学制）2","课程时长21","课程时长22",\
    #             "课程时长31","课程时长32","课程时长41","课程时长42","入学月1","入学月2","入学月3","入学月4",\
    #             "课程费用","课程校区","雅思要求","雅思备注","托福要求","托福备注","面/笔试要求1","面/笔试要求2",\
    #             "工作经验（年）1","工作经验（年）2","作品集1","作品集2","GMAT1","GMAT2","GRE1","GRE2",
    #             "该专业对本地学生要求","英国本地要求展示用"]
    # simple_names = ["专业ID","学院","专业","相关背景要求","课程列表英","官网链接","课程时长1（学制）1","入学月1",\
    #                 "课程费用","雅思要求","雅思备注","面/笔试要求1","面/笔试要求2","工作经验（年）1","工作经验（年）2",\
    #                 "作品集1","作品集2","GMAT1","GMAT2","GRE1","GRE2","该专业对本地学生要求","英国本地要求展示用"]
    # simple_names2 = ["专业ID","专业","官网链接","面/笔试要求1","面/笔试要求2","工作经验（年）1","工作经验（年）2",\
    #                 "作品集1","作品集2"]
    general_names = [
        header.major_id,
        header.region,
        header.school_english_name,
        header.school_chinese_name,
        header.qs_ranking_2023,
        header.qs_ranking_2022,
        header.college,
        header.college_chinese,
        header.major,
        header.major_chinese,
        header.background_requirements,
        header.background_requirements_chinese,
        header.project_intro_chinese,
        header.course_list_chinese,
        header.course_list_english,
        header.website_link,
        header.course_duration_1,
        header.course_duration_2,
        header.course_duration_3,
        header.course_duration_4,
        header.admission_month_1,
        header.admission_month_2,
        header.admission_month_3,
        header.admission_month_4,
        header.course_fee,
        header.course_campus,
        header.ielts_requirement,
        header.ielts_remark,
        header.toefl_requirement,
        header.toefl_remark,
        header.exam_requirements,
        header.exam_requirements_details,
        header.work_experience_years,
        header.work_experience_details,
        header.portfolio,
        header.portfolio_details,
        header.gmat,
        header.gre,
        header.cn_requirement,
        header.uk_requirement,
        header.major_specialization_1,
        header.major_specialization_2,
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
    simple_names = [
        header.major_id,
        header.college,
        header.major,
        header.background_requirements,
        header.course_list_english,
        header.website_link,
        header.course_duration_1,
        header.admission_month_1,
        header.course_fee,
        header.ielts_requirement,
        header.ielts_remark,
        header.exam_requirements,
        header.exam_requirements_details,
        header.work_experience_years,
        header.work_experience_details,
        header.portfolio,
        header.gmat,
        header.gre,
        header.cn_requirement,
        header.uk_requirement
    ]
    simple_names2 = [
        header.major_id,
        header.major,
        header.website_link,
        header.exam_requirements,
        header.exam_requirements_details,
        header.work_experience_years,
        header.work_experience_details,
        header.portfolio,
        header.gmat,
        header.gre
    ]

    if column_type == "general":
        selected_col_names = general_names
    elif column_type == "simple":
        selected_col_names = simple_names2
    else:
        print("无效的列名类型。请选择 'general' 或 'simple'。")
        return

    # 1. 读取两个文件
    standard_data = pd.read_excel(standard_path).copy()
    ourdata = pd.read_excel(ourdata_path).copy()

    # 2. 选取要比对的列
    standard_data = standard_data[selected_col_names]
    ourdata = ourdata[selected_col_names]

    # 3. merge on the basis of the column header.website_link
    # 3.1 为 header.website_link 列添加不同的后缀
    standard_data = standard_data.rename(
        columns={header.website_link: "官网链接_人工"})
    ourdata = ourdata.rename(columns={header.website_link: "官网链接_机器"})

    # 3.2 merge 使用“官网链接”列进行内部连接，得到匹配的数据
    matched_df = pd.merge(ourdata, standard_data, left_on="官网链接_机器",
                          right_on="官网链接_人工", how="inner", suffixes=('_机器', '_人工'))

    # 3.3 使用外部连接得到所有数据，然后从中删除匹配的数据，得到未匹配的数据
    all_df = pd.merge(ourdata, standard_data, left_on="官网链接_机器",
                      right_on="官网链接_人工", how="outer", suffixes=('_机器', '_人工'))
    unmatched_df = all_df[~all_df["官网链接_机器"].isin(
        matched_df["官网链接_机器"]) & ~all_df["官网链接_人工"].isin(matched_df["官网链接_人工"])]
    unmatched_df = unmatched_df.drop(columns=["官网链接_机器", "官网链接_人工"])
    # 3.4 将匹配的数据和未匹配的数据进行垂直拼接
    final_df = pd.concat([matched_df, unmatched_df], axis=0)

    # 3.5. 交叉放置两个表的列
    columns_pro = [col for col in final_df.columns if col.endswith('_机器')]
    columns_ucl = [col for col in final_df.columns if col.endswith('_人工')]
    reordered_columns = []
    for col_pro, col_ucl in zip(columns_pro, columns_ucl):
        reordered_columns.append(col_pro)
        reordered_columns.append(col_ucl)

    final_df = final_df[reordered_columns]

    # 4. 保存合并后的数据表
    final_df.to_excel("output_all.xlsx", index=False)

    # # 5.自定义操作
    # ## 检查两个表的某些项是否一样，不一样输出到wrong_data.xlsx
    # examine_cols = [header.major_id,header.course_fee,header.ielts_requirement,header.cn_requirement,header.uk_requirement,header.admission_month_1,"课程时长1（学制）1"]
    # # 将不一样的数据提取出来
    # different_data = final_df[final_df.apply(lambda x: any(x[col + "_机器"] != x[col + "_人工"] for col in examine_cols), axis=1)]

    # # 将any(x[col + "_机器"] != x[col + "_人工"] 的数据高亮显示出来
    # #TODO
    # # 保存不一样的数据到 Excel 文件
    # different_data.to_excel("wrong_data.xlsx", index=False)


if __name__ == "__main__":
    main()
