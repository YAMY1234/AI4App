import requests
from config.settings import HEADERS, TIMEOUT

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


