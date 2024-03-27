from selenium import webdriver

# 指定WebDriver的路径
driver_path = '/path/to/your/chromedriver'

# 初始化WebDriver
# driver = webdriver.Chrome(driver_path)

def get_cookie(url):
    # 初始化WebDriver
    if driver_path:
        driver = webdriver.Chrome(driver_path)
    else:
        driver = webdriver.Chrome()

    # 访问网页
    driver.get(url)

    # 获取cookies
    cookies = driver.get_cookies()

    # 打印cookies
    # print(cookies)
    return cookies


def format_cookies_for_request_header(cookies):
    """
    将cookie列表转换为适用于requests库的请求头格式。

    参数:
    - cookies (list): 一个包含多个cookie字典的列表。

    返回:
    - str: 格式化的Cookie头字符串。
    """
    cookie_parts = []
    for cookie in cookies:
        # 对于每个cookie字典，取出name和value，并将它们格式化为"name=value"的形式
        part = f"{cookie['name']}={cookie['value']}"
        cookie_parts.append(part)
    # 将所有的"name=value"部分用"; "连接成一个字符串
    cookie_header = "; ".join(cookie_parts)
    return cookie_header

if __name__ == "__main__":
    url = "https://bschool.nus.edu.sg/"
    cookie = get_cookie(url)
    print(format_cookies_for_request_header(cookie))
