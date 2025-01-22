import requests
import json
import pandas as pd
from pandas import json_normalize
import time
from itertools import cycle,zip_longest
import csv
import numpy as np

api_key0 = "RGAPI-b668721a-8b36-4f00-bf87-02a60ea23fce" #뿌구리
api_key1=  "RGAPI-516d4027-ea6e-4986-9e3d-0b85f650d123" #쁘댕이
api_key2=  "RGAPI-a5363f99-402f-46a0-9268-74c9451e0c43" #겸도리
api_keys=[api_key0,api_key1,api_key2]

url=f"https://kr.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={api_key0}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

challenger_matchid=list(pd.read_csv(r'C:\Users\tongk\OneDrive\바탕 화면\GitHuboo\boo\challenger_matchid.csv',encoding='utf-8'))

#챌린저 경기 결과 데이터 가져오기
challenger_game_Data=pd.DataFrame()
count=1
error_count=0
for i,j in zip(challenger_matchid,cycle(api_keys)):
  try:
    url=f"https://asia.api.riotgames.com/tft/match/v1/matches/{i}?api_key={j}"
    x=json.loads(requests.get(url, headers=headers).text)['info']
    game_datetime=x['game_datetime']
    game_version=x['game_version']
    y=pd.DataFrame(x['participants'])
    y.drop(columns=['gold_left','last_round','level','missions','companion','puuid','players_eliminated','time_eliminated','total_damage_to_players'],inplace=True)
    y['game_datetime']=game_datetime
    y['game_version']=game_version
    challenger_game_Data=pd.concat([challenger_game_Data,y])
    time.sleep(0.05)
  except:
    error_count+=1
    continue
  count+=1
  if count%300==0:
    print(f"{count}만큼 추출 완료..쉬는중..")
    time.sleep(115)

#저장
challenger_game_Data=challenger_game_Data.reset_index(drop=True)
challenger_game_Data.to_feather('./challenger_game_Data.feather')
