import requests

def translate_with_token(text, target_language, access_token):
    url = "https://translation.googleapis.com/language/translate/v2"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "q": text,
        "target": target_language,
        "format": "text"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["data"]["translations"][0]["translatedText"]

if __name__ == "__main__":
    text_to_translate = "Hello, world!"
    access_token = "ya29.a0AfB_byCnZIKM5hoyr38yIoRfTPGgfqwco_bbpW271baovXV3wTJKEihqvb4ESsMwBuE1hs6DxFSFdi0fFpOXx5aYjG1379i1SAFBRetxjBxgG6o-PXDsqBsXTA3ml9gtFGwEkpIKvcTRZPHUtFLTk0pOpO9DgNthz-E3hCJnaCgYKATsSARESFQHsvYls5tnJltgN5gNepXgi2c7Mkg0175"  # 从gcloud命令获取的令牌

    translated_text = translate_with_token(text_to_translate, "zh-CN", access_token)
    print(translated_text)