import os
import requests
import urllib3
import json
import google.generativeai as genai
from bs4 import BeautifulSoup

# 1. 處理安全警告：環境部網站憑證有問題時，忽略警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_process():
    # --- 設定區 ---
    target_url = "https://cfp.moenv.gov.tw/WebPage/WebSites/CoefficientDB.aspx"
    api_key = os.environ.get("GEMINI_API_KEY")
    output_file = "data.json"

    if not api_key:
        print("錯誤：找不到 GEMINI_API_KEY 環境變數，請檢查 GitHub Secrets 設定。")
        return

    # --- 第一階段：爬取網頁 ---
    print(f"正在連線至：{target_url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # verify=False 解決 SSL 驗證失敗問題
        response = requests.get(target_url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 取得網頁純文字，並限制長度避免 Gemini Token 溢出
        raw_text = soup.get_text()[:4000] 
        print("網頁資料抓取成功！")

    except Exception as e:
        print(f"抓取網頁失敗：{e}")
        exit(1) # 強制結束並回傳錯誤碼 1

    # --- 第二階段：Gemini AI 處理 ---
    print("正在請求 Gemini 進行資料結構化...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        你是一位專業的資料分析師。請從以下環境部網頁內容中，提取出「碳足跡係數」相關資料。
        
        請嚴格遵守以下規則：
        1. 輸出格式必須是純 JSON 陣列，不要包含任何 markdown 標籤（如 ```json）。
        2. 每個物件包含：name (產品名稱), unit (單位), co2e (係數值), year (公報年份)。
        3. 如果找不到相關欄位，請填入 null。
        4. 只處理你看到的資料，不要捏造。

        內容如下：
        {raw_text}
        """
        
        result = model.generate_content(prompt)
        # 移除 AI 可能誤加的 markdown 語法
        clean_content = result.text.replace('```json', '').replace('```', '').strip()
        
        # 驗證 JSON 格式是否正確
        json_data = json.loads(clean_content)
        
        # --- 第三階段：儲存檔案 ---
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功！資料已寫入至 {output_file}")

    except json.JSONDecodeError:
        print("錯誤：Gemini 回傳的格式不是有效的 JSON。內容如下：")
        print(clean_content)
        exit(1)
    except Exception as e:
        print(f"Gemini 處理過程發生錯誤：{e}")
        exit(1)

if __name__ == "__main__":
    fetch_and_process()
