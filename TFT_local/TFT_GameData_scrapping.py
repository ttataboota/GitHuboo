import requests
import json
import pandas as pd
from pandas import json_normalize
import time
from itertools import cycle,zip_longest
import csv
import numpy as np
from datetime import datetime

#api_key 매일 갱신 필요

tier='master'
today=datetime.now().strftime("%m-%Y-%d")

api_key0 = "RGAPI-e9fa71b5-3b9c-4ee5-9547-afdd88e2cfa8" #뿌구리
api_key1=  "RGAPI-c6d2ec09-0e37-46b5-b442-8a3e5dfb1110" #쁘댕이
api_key2=  "RGAPI-15c6bab8-562f-48eb-85f2-99333f456798" #겸도리
api_keys=[api_key0,api_key1,api_key2]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

#API를 통해 유저 데이터 가져오기
class RiotAPI:
    def __init__(self, api_keys):
        self.api_keys = cycle(api_keys)  # API 키 순환
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "ko-KR",
            "Origin": "https://developer.riotgames.com"
        }

    def get_user_id(self, tier):
        user_id_api=[]
        for i in range(4):
          url = f"https://kr.api.riotgames.com/tft/league/v1/{tier}?queue=RANKED_TFT&api_key={next(self.api_keys)}"
          df = pd.DataFrame(json.loads(requests.get(url, headers=self.headers).text))
          user_id_api.append(json_normalize(df['entries'])[:500])
        print(f"{user_id_api[0].shape[0]}명의 user_id 추출 완료")
        time.sleep(1)
        return user_id_api

    def get_puuid(self, df):
        time.sleep(1)
        error_count=0
        puuid_list = []
        for i in range(df[0].shape[0]):
            api_key = next(self.api_keys)  # API 키 선택
            url = f"https://kr.api.riotgames.com/tft/summoner/v1/summoners/{df[i%3].iloc[i, 0]}?api_key={api_key}"
            
            try:
              puuid = json.loads(requests.get(url, headers=self.headers).text)['puuid']
              puuid_list.append((puuid, api_key))  # (puuid, 사용한 API 키) 저장
              if i%100==0:
                print(f"{i}개의 puuid를 추출 했습니다")
              time.sleep(0.4)
            except:
               error_count+=1
               if error_count>50:
                  print("puuid 추출시 50개 이상의 오류 발생 오류 수정 요망.")
                  break
        
        print("puuid 추출 완료")
        return puuid_list

    def get_match_ids(self, puuid_list):
        time.sleep(1)
        match_ids = []
        for puuid, api_key in puuid_list:  # 저장된 API 키를 사용
            url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={api_key}"
            match_ids.extend(json.loads(requests.get(url, headers=self.headers).text))
            time.sleep(0.4)

        print("match_id 추출 완료")
        match_ids_save = pd.DataFrame(match_ids, columns=["match_id"])
        match_ids_save.to_csv(f"matchid_full.csv", index=False)
        return list(set(match_ids))



#게임 데이터 가져오기
def user_game_data(matchid):

  game_data=pd.DataFrame()
  count=0
  error_count=0
  for i,j in zip(matchid,cycle(api_keys)):
    try:
      url=f"https://asia.api.riotgames.com/tft/match/v1/matches/{i}?api_key={j}"
      data=json.loads(requests.get(url, headers=headers).text)['info']
      data_df=pd.DataFrame(data['participants'])
      data_df.drop(columns=['gold_left','last_round','level','missions','companion','puuid','players_eliminated','time_eliminated','total_damage_to_players'],inplace=True)
      data_df['game_datetime']=data['game_datetime']
      data_df['game_version']=data['game_version']
      game_data=pd.concat([game_data,data_df])
      time.sleep(0.4)
    except:
      error_count+=1
      print(f"match_id : {i} 에서 오류발생")
      if error_count==50:
         print("오류 50개 이상 발생 코드 종료합니다.")
         break
      continue
    count+=1
    if count%1000==0:
       print(f"{count}만큼 추출 완료")

  print(f"총 게임 데이터 {len(matchid)}건 중 {count} 건 추출 완료.")
  #저장
  game_data=game_data.reset_index(drop=True)
  game_data.to_feather(f'data/{tier}_game_data_{today}.feather')
  print(f"{tier}_game data_{today} 추출 완료")

  return game_data


api = RiotAPI(api_keys)
data_user_id = api.get_user_id(tier)
puuid_list = api.get_puuid(data_user_id)  # (puuid, api_key) 쌍 리스트
match_ids = api.get_match_ids(puuid_list)  # 같은 api_key로 match_id 요청

user_game_data(match_ids)

