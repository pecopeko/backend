from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import re

# --- パース専用関数 ---
def parse_datetime_info(datetime_info):
    """ 1件のデータをパースして整理する """
    match = re.match(r"(\d{2})/(\d{2})（(.+)）\s*(\d{2}:\d{2})-(\d{2}:\d{2})", datetime_info)
    if not match:
        raise ValueError(f"パース失敗: {datetime_info}")

    month, day, weekday, start_time, end_time = match.groups()
    date = f"2025-{month}-{day}"  # 年は固定
    return [date, weekday, start_time, end_time]

options = Options()
options.add_argument('--headless')  # 画面に出さない
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# URLアクセス
url = "https://labola.jp/r/shop/3094/calendar_week/"
driver.get(url)

# 明示的待機：カレンダーが表示されるまで最大10秒待つ
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.selected"))
    )
    print("LaBOLAのロゴが表示されました！")
except Exception as e:
    print("ロゴが出てこない...:", e)


records_raw = []

print("空いてる日を探します。")
free_slots = driver.find_elements(By.CSS_SELECTOR, 'td.slot.ex_btn.link.empty.join.not_full.no')

print(len(free_slots))
for slot in free_slots:
    try:
        span = slot.find_element(By.TAG_NAME, 'span')
        p = span.find_element(By.TAG_NAME, 'p')
        
        # innerHTMLを取る（改行タグも取得）
        p_html = p.get_attribute('innerHTML')
        
        # <br>で分割
        parts = p_html.split('<br>')
        
        if len(parts) >= 2:
            datetime_info = parts[1].strip()
            records_raw.append((datetime_info))
    except Exception as e:
        print("データ取得エラー:", e)

# 生データをパースして整形
records_parsed = []
for datetime_info in records_raw:
    try:
        parsed = parse_datetime_info(datetime_info)
        records_parsed.append(parsed)
    except Exception as e:
        print("パースエラー:", e)

# 順番を保ったまま重複を削除
seen = set()
unique_records = []
for row in records_parsed:
    row_tuple = tuple(row)
    if row_tuple not in seen:
        seen.add(row_tuple)
        unique_records.append(row)

# CSVに書き出し
with open('available_slots.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['日付', '曜日', '開始時刻', '終了時刻'])  # ヘッダー
    writer.writerows(unique_records)