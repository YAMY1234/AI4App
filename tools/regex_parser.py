import re

def extract_gpa(text):
    """
    提取GPA信息
    """
    # 示意性的正则匹配
    match = re.search(r'GPA\s*:\s*(\d+\.\d+)', text)
    return match.group(1) if match else None

# 同样的方式添加其他正则提取函数，例如托福、GRE等
