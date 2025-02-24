#%%

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


#내 api key
api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJhMTA2NjVlMC0wMDI5LTAxM2ItMjE3MS0yNzQ4YzRhN2Q1ZDYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjYwNzIwMjQyLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii01NGI0MDRmMy1kZDFhLTQwMzItYWJlMC1mMGU5ZWE3NDQxNzUifQ.wNUumN93avLiYsfnAv3JAJycd4V2jcxWdFOzgqNmVcc'
platform='steam'
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/vnd.api+json"
}



match_id_list=[]

player_name = 'iFTY_HuaHai'

url = f"https://api.pubg.com/shards/{platform}/players?filter[playerNames]={player_name}"

# 🔹 API 요청
response = requests.get(url, headers=headers)

# 🔹 응답 확인
if response.status_code == 200:
    data = response.json()
    match_ids = [match["id"] for match in data["data"][0]["relationships"]["matches"]["data"]]  # 최근 매치 ID 리스트
    match_id_list.extend(match_ids)
else:
    print("에러 발생")
    

match_id_list=list(set(match_id_list))[:10]
match_id_list = pd.DataFrame(match_id_list, columns=["match_id"])
match_id_list.to_csv(f"iFTY_HuaHai_match_id_list.csv", index=False)



