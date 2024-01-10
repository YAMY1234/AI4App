import requests
import json
import pandas as pd


def download_html(url):
    url = "https://vis90prd.hkmu.edu.hk/psc/s90prdp/EMPLOYEE/SA/s/WEBLIB_WPREG.ISCRIPT1.FieldFormula.IScript_GetPGProgrammes?&sm=non_local&sm=ft&"

    # 请求头部
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://admissions.hkmu.edu.hk',
        'Referer': 'https://admissions.hkmu.edu.hk/sc/tpg/programmes/',
        'X-Requested-With': 'XMLHttpRequest',
        # 其他必要的头信息...
    }
    # Cookies
    cookies = {
        # 'ApplicationGatewayAffinityCORS': 'a29b502e44733636d6c2f16984ebb87b',
        # 'ApplicationGatewayAffinity': 'a29b502e44733636d6c2f16984ebb87b',
        # '_lscache_vary': 'e5a3f82d1ee3f4191f6d1dd0a887a59f',
        # ...其他必要的cookies
    }

    # POST请求的数据（如果有的话）
    data = {
        # 需要发送的数据...
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    if response.status_code == 200:
        print("成功获取数据")
        return response.text  # 或者 response.json()，如果响应是JSON格式的
    else:
        print("获取数据失败，状态码：", response.status_code)


def crawl():
    # 网址
    url = "https://vis90prd.hkmu.edu.hk/psc/s90prdp/EMPLOYEE/SA/s/WEBLIB_WPREG.ISCRIPT1.FieldFormula.IScript_GetPGProgrammes?&sm=non_local&sm=ft&"

    # 发送请求获取数据
    resp_text = download_html(url)
    print(resp_text)

    # 解析JSON数据
    data = json.loads(resp_text)

    # 提取项目名称和URL
    program_list = []
    for item in data:
        program_name = item.get("OURUT_PDESC_E", "")
        url_link = item.get("OURUT_URL_ENG", "")
        program_list.append({"ProgramName": program_name, "URL Link": url_link})

    # 创建DataFrame
    df = pd.DataFrame(program_list)

    # 保存到Excel
    df.to_excel("programs.xlsx", index=False)

    print("Excel file 'programs.xlsx' has been created with the program names and URLs.")

if __name__ == '__main__':
    crawl()