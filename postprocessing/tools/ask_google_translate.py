import os
import pandas as pd

import requests
import time

def is_null(text):
    if isinstance(text, str):
        if len(text) == 0:
            return True
    else:
        print("not a text type")
        return True

def translate_text(text, target_language="zh", source_language="en", api_key="AIzaSyAmnp8pnz8QKRvnPfLKhl5aPA3teKE122o"):
    """
    Translates the input text using Google Cloud Translation API.

    Parameters:
        text (str): The input text to translate.
        target_language (str): The language to use for translation.
        source_language (str, optional): The language of the source text.
        api_key (str): Your Google Cloud API key.

    Returns:
        str: Translated text.
    """
    if is_null(text):
        return ""

    base_url = "https://translation.googleapis.com/language/translate/v2"
    payload = {
        "q": text,
        "target": target_language,
        "format": "text",
        "key": api_key
    }
    if source_language:
        payload["source"] = source_language

    max_retries = 3
    retries = 0

    while retries < max_retries:
        response = requests.post(base_url, data=payload)

        # If request is successful, return translated text
        if response.status_code == 200:
            translated_data = response.json()
            translated_text = translated_data["data"]["translations"][0]["translatedText"]
            print(translated_text)
            return translated_text
        else:
            print(f"Error {response.status_code}: {response.text}. Retrying...")
            retries += 1
            time.sleep(2)

    raise Exception("Failed to translate text after maximum retries")


def ask_api_to_translate(school_abbr, col_name, translated_col_name):
    # Load the Excel file into a DataFrame
    program_details_stage1_path = f"data/{school_abbr}/program_details_stage1.xlsx"
    program_details_stage2_path = f"data/{school_abbr}/program_details_stage2.xlsx"

    if "program_details_stage2.xlsx" in os.listdir(f'data/{school_abbr}'):
        df_program_details = pd.read_excel(program_details_stage2_path)
    else:
        df_program_details = pd.read_excel(program_details_stage1_path)

    for index, row in df_program_details.iterrows():
        original_text = row[col_name]
        # 如果是空的话才转换
        if is_null(row[translated_col_name]):
            translated_text = translate_text(original_text)
            df_program_details.at[index, translated_col_name] = translated_text

    # Save the modified DataFrame back to the Excel file
    df_program_details.to_excel(program_details_stage2_path, index=False)