import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import urllib3

# 1. 配置 Gemini (從環境變數讀取 Key)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash') # 使用 Flash 版本速度快且免費額度高

def fetch_carbon_data():
    # 2. 抓取環境部網頁 HTML
    url = "https://cfp.moenv.gov.tw/WebPage/WebSites/CoefficientDB.aspx"
    headers = {'User-Agent': 'Mozilla/5.0'}
   verify_ssl = os.getenv('VERIFY_SSL', 'true').lower() == 'true'

    response = requests.get(
        'https://cfp.moenv.gov.tw/WebPage/WebSites/CoefficientDB.aspx',
        verify=verify_ssl
    )
    response.encoding = 'utf-8' # 確保中文不亂碼
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. 取得表格內容 (這裡我們抓取前 3000 字元，避免超出 AI 單次處理量)
    # 註：這是一個示範，精確做法是定位 table 標籤
    table_content = soup.get_text()[:3000] 

    # 4. 設計 Prompt 讓 Gemini 輸出標準格式
    prompt = f"""
    你現在是一個資料分析師。請從以下網頁文字中提取『產品碳足跡係數』資料。
    請輸出為一個 JSON 陣列，格式如下：
    [
      {{"name": "產品名稱", "unit": "單位", "coefficient": "數值", "year": "年份"}}
    ]
    只輸出 JSON 內容，不要包含任何說明文字。
    內容如下：
    {table_content}
    """
    
    try:
        result = model.generate_content(prompt)
        # 清理可能夾雜的 ```json 標籤
        clean_json = result.text.replace('```json', '').replace('```', '').strip()
        
        # 5. 儲存成檔案
        with open('data.json', 'w', encoding='utf-8') as f:
            f.write(clean_json)
        print("資料更新成功！")
        
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_carbon_data()
