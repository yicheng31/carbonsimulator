import requests
import os
import json

# API Key 從環境變數讀取 (GitHub Actions 會提供)
API_KEY = os.getenv("MOENV_API_KEY")

# 定義要抓取的資料集
DATASETS = {
    "transport": "CFP_P_01",  # 交通運輸係數
    "products": "CFP_P_02"    # 產品碳足跡 (包含食材)
}

def fetch_data(data_id):
    url = f"https://data.moenv.gov.tw/api/v2/{data_id}"
    params = {
        "api_key": API_KEY,
        "format": "json",
        "limit": 1000  # 增加抓取筆數
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("records", [])
    else:
        print(f"抓取 {data_id} 失敗: {response.status_code}")
        return []

def main():
    all_data = {}
    for category, data_id in DATASETS.items():
        print(f"正在同步 {category} 資料...")
        all_data[category] = fetch_data(data_id)

    # 存成 JSON 檔供專案呼叫
    with open('carbon_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("同步完成！")

if __name__ == "__main__":
    main()
