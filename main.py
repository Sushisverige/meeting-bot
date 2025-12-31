import os
import datetime
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from notion_client import Client
import google.generativeai as genai
from dotenv import load_dotenv

# ローカル実行用（GitHub Actions上では無視されます）
load_dotenv()

# --- 設定（環境変数から取得） ---
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = 'google_credential.json'

CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# 初期設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')
notion = Client(auth=NOTION_TOKEN)

def get_todays_events():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    now_utc = datetime.datetime.utcnow()
    now_jst = now_utc + datetime.timedelta(hours=9)
    start_jst = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)
    end_jst = now_jst.replace(hour=23, minute=59, second=59, microsecond=0)
    time_min = (start_jst - datetime.timedelta(hours=9)).isoformat() + 'Z'
    time_max = (end_jst - datetime.timedelta(hours=9)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=time_min, timeMax=time_max,
        singleEvents=True, orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def generate_summary(title, desc):
    prompt = f"会議名: {title}\n詳細: {desc}\nこの会議の議事録テンプレートをMarkdown形式で作成してください。項目: 目的, アジェンダ案, ToDo。"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI生成エラー: {e}"

def create_notion(title, content):
    page_id = NOTION_PAGE_ID.replace("-", "")
    notion.pages.create(
        parent={"page_id": page_id},
        properties={"title": {"title": [{"text": {"content": title}}]}},
        children=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "AI議事録"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": content[:2000]}}]}}
        ]
    )

def main():
    try:
        events = get_todays_events()
        if not events:
            print("本日の予定はありません。")
            return
        for event in events:
            summary = event.get('summary', 'タイトルなし')
            desc = event.get('description', '詳細なし')
            print(f"処理中: {summary}")
            ai_text = generate_summary(summary, desc)
            create_notion(f"【議事録】{summary}", ai_text)
            requests.post(SLACK_WEBHOOK_URL, json={"text": f"📅 議事録を作成しました！\n会議: {summary}"})
        print("全ての処理が完了しました。")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
