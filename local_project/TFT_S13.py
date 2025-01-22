import requests
import json
import pandas as pd
from pandas import json_normalize
import time
from itertools import cycle,zip_longest
import csv
import numpy as np

#api_key 매일 갱신 필요

api_key0 = "RGAPI-b668721a-8b36-4f00-bf87-02a60ea23fce" #뿌구리
api_key1=  "RGAPI-1826d62b-e7e6-4807-8518-a0e13d865aeb" #쁘댕이
api_key2=  "RGAPI-4a01e30b-dfae-4966-8016-a494cdd148f0" #겸도리
api_keys=[api_key0,api_key1,api_key2]

url=f"https://kr.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={api_key0}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

#df에는 entries를 제외하고 유용한 데이터 없음 전부 같은 데이터
df=pd.DataFrame(json.loads(requests.get(url, headers=headers).text))

#entries 에 있는 데이터 중첩 풀어서 df로 변환
challenger_df = json_normalize(df['entries'])

print("challenger_df 추출 완료")

#챌린저 암호화된 소환사id->puuid
challenger_puuid=[]
count=1
for i in range(challenger_df.shape[0]):
  url=f"https://kr.api.riotgames.com/tft/summoner/v1/summoners/{challenger_df.iloc[i,0]}?api_key={api_key0}"
  headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
          }
  p=json.loads(requests.get(url, headers=headers).text)['puuid']
  challenger_puuid.append(p)
  time.sleep(0.05)
  count+=1
  if count%100==0:
    print(f"puuid 추출중... {count} 개 만큼 추출 완료 ")
    time.sleep(116)



#puuid를 통해서 최근 20경기 매치를 뽑아낸다
count=1
challenger_matchid=[]
for i in challenger_puuid:
  url=f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{i}/ids?start=0&count=20&api_key={api_key0}"
  headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
          }
  match_id=json.loads(requests.get(url, headers=headers).text)
  challenger_matchid.extend(match_id)
  time.sleep(0.05)
  count+=1
  if count%100==0:
    print(f"matchid 추출중... {count} 개 만큼 추출 완료 ")
    time.sleep(115)
challenger_matchid=list(set(challenger_matchid))

#챌린저 match_id 리스트 저장

with open('challenger_matchid.csv','w',newline='') as file:
  writer = csv.writer(file)
  writer.writerow(challenger_matchid)
print("끝!")