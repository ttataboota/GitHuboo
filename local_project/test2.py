import requests
import json
import pandas as pd
from pandas import json_normalize
import time
from itertools import cycle,zip_longest
import csv
import numpy as np



# 현 시즌 설정
now_season = 13


json_files = {
    "trait": "tft-trait.json",
    "champion": "tft-champion.json",
    "item": "tft-item.json",
    "augments": "tft-augments.json"
}

#data_dragon 데이터 모일곳
data_dragon = {}

for key, filename in json_files.items():
    with open(filename, 'r', encoding='utf-8') as json_file:
        data_dragon[key] = json.load(json_file)



data_dragon_dict = {
    "trait": data_dragon["trait"],
    "champion": data_dragon["champion"],
    "item": data_dragon["item"],
    "augments": data_dragon["augments"]
}

# 한글 딕셔너리
dic_eng_kor = {}

for key, data in data_dragon_dict.items():
    df = pd.DataFrame(data['data'])  
    df_eng_kor = df.iloc[0:2, :]  # 영어-한국어 매핑
    dic_temp = {df_eng_kor.iloc[0, i]: df_eng_kor.iloc[1, i] for i in range(df_eng_kor.shape[1])} 
    if key=='item':
       dic_eng_kor[key] = {k: v for k, v in dic_temp.items()}  # item 은 시즌 지나도 재활용해서 시즌필터링 x
    else:
        dic_eng_kor[key] = {k: v for k, v in dic_temp.items() if f'TFT{now_season}' in k}  # 시즌 필터링



df_champ_usage = pd.read_csv('./df_champ_usage.csv')


df_champ_usage.columns=df_champ_usage.columns.map(dic_eng_kor['champion'])

df_champ_usage.to_csv("df_champ_usage.csv", index=False, encoding="utf-8-sig")