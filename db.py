import pandas as pd
import requests

# --- Supabase設定 ---
supabase_url = "https://glpnlarhekitkrebnxmn.supabase.co"  # あなたのURL
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdscG5sYXJoZWtpdGtyZWJueG1uIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTkwOTMzMywiZXhwIjoyMDYxNDg1MzMzfQ.gGLkrvJlhq-GG7AiZoZRKvMgc_yP5UMR_Q0_IGj3A34"              # あなたのAPIキー
table_name = "available"               # あなたのテーブル名
stadium_id = "18b90571-4b17-452a-b4b6-87d7edb9f598"                            # ← ここで固定！スタジアムID

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- CSV読み込み ---
csv_path = "available_slots.csv"  # CSVファイルのパス
df = pd.read_csv(csv_path)

# --- 曜日列を無視して必要な列だけ取り出す ---
df = df[['日付', '開始時刻', '終了時刻']]
df.columns = ['date', 'start_time', 'end_time']

# --- stadium_id列を追加する ---
df['stadium_id'] = stadium_id

# --- データを1行ずつインサート ---
for index, row in df.iterrows():
    data = row.to_dict()
    response = requests.post(
        f"{supabase_url}/rest/v1/{table_name}",
        json=data,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"{index+1}行目：成功")
    else:
        print(f"{index+1}行目：失敗 ({response.status_code}) {response.text}")
