import requests
from config.settings import HEADERS, TIMEOUT
import time
from utils.logger import setup_logger


def fetch_url_content(url):
    """
    根据URL抓取内容
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()  # 如果请求失败，这将引发异常
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None



def request_with_retry(url, method='GET', headers=None, data=None, params=None, max_retries=3, delay=10,
                       school_name=None):
    retries = 0

    # 初始化logger
    logger = None
    if school_name:
        logger = setup_logger(school_name)

    while retries <= max_retries:
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # 如果返回的HTTP状态码不是200-399，它将引发一个HTTPError。
            return response
        except (requests.ConnectionError, requests.HTTPError) as e:
            print(f"Warning: requests.ConnectionError raised {retries+1} times for url: {url}")
            retries += 1
            if retries > max_retries:
                error_msg = f"{method} request error for URL {url} after {max_retries} retries: {e}"
                print(error_msg)
                if logger:
                    logger.error(error_msg)
                return
            time.sleep(delay)

