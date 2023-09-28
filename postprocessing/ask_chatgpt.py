import openai

def query_gpt3(prompt):
    # 设置你的API密钥
    openai.api_key = "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"

    # 创建API请求
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # 返回API的回复内容
    return response['choices'][0]['message']['content']

# # 使用这个函数
# response_content = query_gpt3("怎么申请visa信用卡")
# print(response_content)

def query_gpt3_deadline(data):
    content = "data是"+data + "。要求是输出【入学季】-【开放时间】-【截止时间】，比如【9月-2023.9.1-2024.2.9】，\
    方便系统识别；注意1月直接写1，比如2024.1.5，不写2024.01.05；\
    如果没有开放时间，则开放时间为一个空格，比如【9月- -2024.2.9】；\
    如果没有截止时间，则【9月-2023.6.19-无明确申请截止日期】\
    如果没有开放时间和截止时间，则【9月- -无明确申请截止日期】"
    return query_gpt3(content)

# print(query_gpt3_deadline(""))