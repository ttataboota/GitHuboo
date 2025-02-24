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

df=pd.read_csv('match_id_list.csv')
match_id = df['match_id'].tolist()

match_id=match_id[:1]

data=[]

for i in match_id:
    url = f"https://api.pubg.com/shards/{platform}/matches/{i}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        match_data = response.json()
        print("✅ 매치 정보 가져오기 성공!")
    else:
        print(f"❌ 요청 실패: {response.status_code}, {response.text}")

#%%
    match_data_df=pd.DataFrame(match_data['included'])
    player=match_data_df[match_data_df['type']=='participant']['attributes']

    for i in player:
        data.append(i['stats'])



data_df=pd.DataFrame(data)
data_df

data_df.to_csv("data_df.csv", index=False)