from datetime import datetime
import os
import warnings

import pandas as pd
import requests
from bs4 import BeautifulSoup            # 备用
from DDLNotifier.email_sender import send_email
from DDLNotifier.config import CONFIG
from DDLNotifier.utils.compare_and_notify import compare_and_notify

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
URL = "https://www.ntu.edu.sg/admissions/graduate/cwadmissionguide/apply-now"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH_EXCEL = os.path.join(BASE_PATH, "programme_data.xlsx")
# recipient_email = CONFIG.RECIPEINT_EMAIL
recipient_email = "yamy12344@gmail.com"

school_name = BASE_PATH.split("_")[-1]
log_file = os.path.join(BASE_PATH, "notification_log.txt")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def download_html(url: str) -> str:
    """
    Fetch raw HTML from target URL.
    """
    # 可按需设置 headers
    response = requests.get(url, headers=None, timeout=30, verify=False)
    response.raise_for_status()
    return response.text


def _extract_programme_table(html: str) -> pd.DataFrame:
    """
    从页面里挑出包含 “Programme Name” 的那张表。带 DEBUG 打印。
    """
    warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

    # header=0 让第一行作为列名
    candidate_tables = pd.read_html(html, flavor="lxml", header=0)
    print(f"[DEBUG] 共解析出 {len(candidate_tables)} 张 <table>")

    for idx, tbl in enumerate(candidate_tables):
        print(f"[DEBUG] 表 {idx} 列名: {list(tbl.columns)}")
        if "Programme Name" in tbl.columns and "Opening Date" in tbl.columns:
            print(f"[DEBUG] 选用表 {idx} 作为目标表")
            print(tbl.head(3))            # 打印样例行
            return tbl

    print("[DEBUG] 未找到包含 'Programme Name' 的表")
    return pd.DataFrame()


def parse_html(html: str) -> pd.DataFrame:
    """
    解析 HTML，返回 [Programme, Deadline] 两列。
    Deadline 格式: 'Opening Date to Closing Date'
    """
    df = _extract_programme_table(html)
    if df.empty:
        return df

    # 修补 rowspan 产生的 NaN
    if "Admission Year & Intake" in df.columns:
        df["Admission Year & Intake"].ffill(inplace=True)

    # 去掉无效行
    df = df[df["Programme Name"].notna() & df["Opening Date"].notna()]

    # 标准化字符串
    df["Opening Date"] = df["Opening Date"].astype(str).str.strip()
    df["Closing Date"] = df["Closing Date"].astype(str).str.strip()

    df["Deadline"] = df["Opening Date"] + " to " + df["Closing Date"]
    result = df[["Programme Name", "Deadline"]].copy()
    result.columns = ["Programme", "Deadline"]

    print("[DEBUG] 解析完成的 DataFrame：")
    print(result.head())

    return result


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------
def main() -> None:
    print("Downloading HTML...")
    new_html = download_html(URL)

    print("Parsing HTML...")
    new_data = parse_html(new_html)

    if new_data.empty:
        print("⚠️  未解析到任何可用数据，可能页面结构再次改变。")
        return

    if os.path.exists(SAVE_PATH_EXCEL):
        old_data = pd.read_excel(SAVE_PATH_EXCEL)
    else:
        old_data = pd.DataFrame()

    compare_and_notify(old_data, new_data, log_file, school_name)
    new_data.to_excel(SAVE_PATH_EXCEL, index=False)
    print(f"✅  数据已更新并保存至 {SAVE_PATH_EXCEL}")


if __name__ == "__main__":
    main()
