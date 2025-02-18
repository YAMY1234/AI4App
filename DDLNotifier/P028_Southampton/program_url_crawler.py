from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin
import requests


def crawl(url="https://www.southampton.ac.uk/courses/postgraduate?keyword_filter="):
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有包含data-course-name属性的<li>元素
    li_elements = soup.find_all('li', class_='course-list-item', attrs={'data-course-name': True})

    data = {'ProgramName': [], 'URL Link': []}
    base_url = "https://www.southampton.ac.uk"

    for li in li_elements:
        # 提取data-course-name属性作为项目名称
        program_name = li.get('data-course-name', 'No Program Name')

        # 查找<li>内的<a>标签并获取href属性
        a_tag = li.find('a', href=True)
        if a_tag:
            program_link = a_tag['href']
            full_url = urljoin(base_url, program_link)  # 形成完整的URL

            # 将提取的数据添加到字典中
            data['ProgramName'].append(program_name)
            data['URL Link'].append(full_url)
        else:
            print(f"在<li>元素中未找到<a>标签，项目名称: {program_name}")

    # 检查是否有提取到数据并保存到Excel
    if data['ProgramName']:
        try:
            # 创建DataFrame
            df = pd.DataFrame(data)

            # 对DataFrame做额外处理：
            # 对于相同的ProgramName，如果存在多个项目，则只保留URL Link以"msc"结尾的那一项（如果存在多个，则保留第一个）
            def choose_row(group):
                msc_rows = group[group['URL Link'].str.endswith('msc')]
                if not msc_rows.empty:
                    return msc_rows.iloc[[0]]  # 只保留第一个满足条件的项目
                return group.iloc[[0]]  # 如果没有符合条件的，则保留该组中的第一个项目

            df_filtered = df.groupby('ProgramName', as_index=False, group_keys=False).apply(choose_row).reset_index(
                drop=True)

            # 定义Excel文件的保存路径
            PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'programs.xlsx')

            # 保存处理后的DataFrame到Excel文件
            df_filtered.to_excel(PROGRAM_DATA_EXCEL, index=False)
            print(f"数据已成功保存到Excel。总共找到的项目数量: {len(df_filtered)}")
        except Exception as e:
            print(f"保存到Excel时出错: {e}")
    else:
        print("未提取到任何数据。请检查选择器和页面结构。")


if __name__ == '__main__':
    crawl()

