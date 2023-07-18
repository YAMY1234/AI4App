import json
from openpyxl import Workbook

# 读取JSON文件
with open('data/NEU_demo.json', 'r') as file:
    json_data = json.load(file)

# 创建Excel工作簿和工作表
workbook = Workbook()
sheet = workbook.active

# 写入标题行
sheet.append(['Word'])
sheet_words = []
# 提取标题单词并写入Excel表格
for program in json_data['programs']:
    title = program['title']
    words = title.split(' ')

    # 筛选长度大于等于5个字符的单词
    words = [word for word in words if len(word) >= 4]

    # 写入单词行
    for word in words:
        sheet_words.append(word)

sheet_words = list(set(sheet_words))
for word in sheet_words:
    sheet.append([word])
# 保存Excel文件
workbook.save('./data/program_word_bank.xlsx')