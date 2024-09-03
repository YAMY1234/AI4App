'''
要求：
要求写一个爬虫,排取对应URL链接下面的所有Program的URL link,将ProgramName和URL link分别作为两个字段,也就是表头,然后存储在一个Excel表格当中,也就是说第一列是ProgramName,第二列是URL link, 这个URL link就是对应的这个Program对应的URL。

URL:
https://prog-crs.hkust.edu.hk/pgprog/print_result.php?t=1703812719852&token_post=8551fa5718176bc683d62dbeaaf9f305&is_s=Y&keyword=&check-all-degree-option=undefined&check-allsub-degree-option1=undefined&check-allsub-degree-option2=Y&school[]=SSCI&school[]=SENG&school[]=SBM&school[]=SHSS&school[]=IPO&area[]=1&area[]=7&area[]=11&area[]=12&area[]=3&area[]=13&area[]=14&area[]=8&area[]=9&area[]=10&degree[]=DBA&degree[]=MBA&degree[]=MSC&degree[]=MA&degree[]=MPM&degree[]=MPP&degree[]=PGD&year=2024-25

格式如下：
<div class="school"><div class="school-title">School of Science</div><ul class="program-list"><li class="program program-prefix-A program-prefix-C"><a href="/pgprog/2024-25/msc-anchem/" title="Analytical Chemistry"><div class="program-school">Chemistry</div><div class="program-name">Analytical Chemistry</div><div class="program-degree">MSc</div></a></li><li class="program program-prefix-B">

'''
import os.path

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
PROGRAM_DATA_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs.xlsx')
def crawl():
    # 网页 URL
    # url = "https://prog-crs.hkust.edu.hk/pgprog/print_result.php?t=1703812719852&token_post=8551fa5718176bc683d62dbeaaf9f305&is_s=Y&keyword=&check-all-degree-option=undefined&check-allsub-degree-option1=undefined&check-allsub-degree-option2=Y&school[]=SSCI&school[]=SENG&school[]=SBM&school[]=SHSS&school[]=IPO&area[]=1&area[]=7&area[]=11&area[]=12&area[]=3&area[]=13&area[]=14&area[]=8&area[]=9&area[]=10&degree[]=DBA&degree[]=MBA&degree[]=MSC&degree[]=MA&degree[]=MPM&degree[]=MPP&degree[]=PGD&year=2024-25"
    # url = "https://prog-crs.hkust.edu.hk/pgprog/2025-26?token_post=57b738b4f108fdc9e1b7b0dbf9344c36&is_s=Y&keyword=&school%5B%5D=SSCI&school%5B%5D=SENG&school%5B%5D=SBM&school%5B%5D=SHSS&school%5B%5D=IPO&area%5B%5D=1&area%5B%5D=7&area%5B%5D=11&area%5B%5D=12&area%5B%5D=3&area%5B%5D=13&area%5B%5D=14&area%5B%5D=8&area%5B%5D=9&area%5B%5D=10&check-allsub-degree-option2=Y&degree%5B%5D=DBA&degree%5B%5D=MBA&degree%5B%5D=MSC&degree%5B%5D=MA&degree%5B%5D=MPM&degree%5B%5D=MPP&degree%5B%5D=PGD&year=2025-26"
    url = "https://prog-crs.hkust.edu.hk/pgprog/print_result.php?t=1725336874472&token_post=ab2772a59307c08748071513d6b6751f&is_s=Y&keyword=&check-all-degree-option=undefined&check-allsub-degree-option1=undefined&check-allsub-degree-option2=Y&school[]=SSCI&school[]=SENG&school[]=SBM&school[]=SHSS&school[]=IPO&area[]=1&area[]=7&area[]=11&area[]=12&area[]=3&area[]=13&area[]=14&area[]=8&area[]=9&area[]=10&degree[]=DBA&degree[]=MBA&degree[]=MSC&degree[]=MA&degree[]=MPM&degree[]=MPP&degree[]=PGD&year=2025-26"

    # 发送请求
    response = requests.get(url, verify=False)

    # 解析 HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # 寻找所有 Program
    programs = soup.find_all('li', class_='program')

    # 提取 Program 名称和链接
    data = []
    for program in programs:
        program_name = program.find('div', class_='program-name').text.strip()
        program_link = "https://prog-crs.hkust.edu.hk" + program.find('a')['href']
        data.append([program_name, program_link])

    # 创建 DataFrame
    df = pd.DataFrame(data, columns=['ProgramName', 'URL Link'])

    # 保存到 Excel 文件
    df.to_excel(PROGRAM_DATA_EXCEL, index=False)


if __name__ == "__main__":
    crawl()