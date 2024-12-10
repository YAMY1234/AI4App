import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')


def crawl(
        url="https://portal.hku.hk/SavedQueryService/Execute/any-faculty-programmes/%/629270000/1.00/10.00/hkutgp_feeforlocalstudent/0.00/1000000.00"):
    try:
        # 发送GET请求并获取JSON响应
        response = requests.get(url, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        data_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return
    except ValueError:
        print("无法解析JSON响应")
        return

    # 创建一个空的字典来存储课程信息
    data = {"ProgramName": [], "URL Link": []}

    # 遍历JSON数据中的每个项目
    for item in data_json.get("data", []):
        attributes = item.get("Attributes", {})
        program_name = attributes.get("hkutgp_name")
        seofriendlyname = attributes.get("hkutgp_seofriendlyname")

        if program_name and seofriendlyname:
            # 构建新的URL
            program_url = f"https://portal.hku.hk/tpg-admissions/programme-details?programme={seofriendlyname}&mode=0"

            # 将信息添加到字典中
            data["ProgramName"].append(program_name)
            data["URL Link"].append(program_url)

    # 检查是否有数据
    if not data["ProgramName"]:
        print("没有找到任何课程信息")
        return

    # 创建DataFrame
    df = pd.DataFrame(data)

    try:
        # 将数据保存到Excel文件
        df.to_excel(PROGRAM_DATA_EXCEL, index=False)
        print(f"数据已成功保存到 {PROGRAM_DATA_EXCEL}")
    except Exception as e:
        print(f"保存到Excel时出错: {e}")


# 调用爬虫函数
if __name__ == '__main__':
    crawl()
