class ProgramHeader:
    def __init__(self):
        # 为每个英文名创建属性并初始化为空字符串
        self.major_id = ""
        self.region = ""
        self.school_english_name = ""
        self.school_chinese_name = ""
        self.qs_ranking_2023 = ""
        self.qs_ranking_2022 = ""
        self.college = ""
        self.college_chinese = ""
        self.major = ""
        self.major_chinese = ""
        self.background_requirements = ""
        self.background_requirements_chinese = ""
        self.project_intro = ""
        self.project_intro_chinese = ""
        self.course_description_english = ""
        self.course_list_english = ""
        self.course_list_chinese = ""
        self.website_link = ""
        self.course_duration_1 = ""
        self.course_duration_2 = ""
        self.course_duration_3 = ""
        self.course_duration_4 = ""
        self.admission_month_1 = ""
        self.admission_month_2 = ""
        self.admission_month_3 = ""
        self.admission_month_4 = ""
        self.application_deadlines = ""
        self.course_fee = ""
        self.course_campus = ""
        self.ielts_requirement = ""
        self.ielts_remark = ""
        self.toefl_requirement = ""
        self.toefl_remark = ""
        self.exam_requirements = ""
        self.exam_requirements_details = ""
        self.work_experience_years = ""
        self.work_experience_details = ""
        self.portfolio = ""
        self.portfolio_details = ""
        self.gmat = ""
        self.gre = ""
        self.cn_requirement = ""
        self.uk_requirement = ""
        self.major_specialization_1 = ""
        self.major_specialization_2 = ""
        self.major_specialization_3 = ""
        self.major_specialization_4 = ""
        self.major_specialization_5 = ""
        self.major_specialization_6 = ""
        self.major_specialization_7 = ""
        self.major_specialization_8 = ""
        self.major_specialization_9 = ""
        self.major_specialization_10 = ""
        self.major_specialization_11 = ""
        self.major_specialization_12 = ""
        self.major_specialization_13 = ""
        self.major_specialization_14 = ""
        self.ordered_list = []

    def initiate_headers(self, header_info):
        for attr, value in header_info.items():
            setattr(header, attr, value)
        self.ordered_list = list(header_info.values())


header_info = {
    "major_id": "专业ID",
    "region": "地区",
    "school_english_name": "学校英文名",
    "school_chinese_name": "学校中文名",
    "qs_ranking_2023": "QS排名2023",
    "qs_ranking_2022": "QS排名2022",
    "college": "学院",
    "college_chinese": "学院中文",
    "major": "专业",
    "major_chinese": "专业中文",
    "background_requirements": "相关背景要求",
    "background_requirements_chinese": "相关背景要求中",
    "project_intro": "项目简介",
    "project_intro_chinese": "项目简介中",
    "course_description_english": "课程介绍英",
    "course_list_english": "课程列表英",
    "course_list_chinese": "课程列表中",
    "website_link": "官网链接",
    "course_duration_1": "课程时长1(学制)",
    "course_duration_2": "课程时长2",
    "course_duration_3": "课程时长3",
    "course_duration_4": "课程时长4",
    "admission_month_1": "入学月1",
    "admission_month_2": "入学月2",
    "admission_month_3": "入学月3",
    "admission_month_4": "入学月4",
    "application_deadlines": "申请截止日期",
    "course_fee": "课程费用",
    "course_campus": "课程校区",
    "ielts_requirement": "雅思要求",
    "ielts_remark": "雅思备注",
    "toefl_requirement": "托福要求",
    "toefl_remark": "托福备注",
    "exam_requirements": "面/笔试要求",
    "exam_requirements_details": "面/笔试要求细则",
    "work_experience_years": "工作经验（年）",
    "work_experience_details": "工作经验细则",
    "portfolio": "作品集",
    "portfolio_details": "作品集细则",
    "gmat": "GMAT",
    "gre": "GRE",
    "cn_requirement": "该专业对本地学生要求",
    "uk_requirement": "英国本地要求展示用",
    "major_specialization_1": "专业细分方向1",
    "major_specialization_2": "专业细分方向2",
    "major_specialization_3": "专业细分方向3",
    "major_specialization_4": "专业细分方向4",
    "major_specialization_5": "专业细分方向5",
    "major_specialization_6": "专业细分方向6",
    "major_specialization_7": "专业细分方向7",
    "major_specialization_8": "专业细分方向8",
    "major_specialization_9": "专业细分方向9",
    "major_specialization_10": "专业细分方向10",
    "major_specialization_11": "专业细分方向11",
    "major_specialization_12": "专业细分方向12",
    "major_specialization_13": "专业细分方向13",
    "major_specialization_14": "专业细分方向14"
}


# 创建一个SchoolInfo对象
header = ProgramHeader()
header.initiate_headers(header_info)

# print(header.ordered_list)