import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

api_key = os.getenv("API_KEY")


platform='steam'

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/vnd.api+json"
}

df=pd.read_csv('match_id_list.csv')
match_id = df['match_id'].tolist()

telemetry_url_list=[]

count=0
error_count=0

for i in match_id:
    match_url = f"https://api.pubg.com/shards/{platform}/matches/{i}"

    response = requests.get(match_url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()

        # 🔹 Telemetry URL 가져오기
        telemetry_url = next(
            (asset["attributes"]["URL"] for asset in match_data["included"] if asset["type"] == "asset"), 
            None
        )

        telemetry_url_list.append(telemetry_url)

        count+=1

        if count%100==0:
            sys.stdout.write(f"\r{count}개 추출 완료")
            sys.stdout.flush()  # 즉시 출력

    else:
        error_count+=1
        print(f"오류 발생! error_count:{error_count}")


telemetry_url_data=pd.DataFrame(telemetry_url_list,columns=['telemetry_url'])
telemetry_url_data.to_csv("data/telemetry_url_data.csv", index=False)

