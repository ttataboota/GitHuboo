#%%
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
import math
import time
from datetime import date
import csv
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import pickle
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from datetime import date, timedelta
from itertools import cycle
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

api_key1 = os.getenv("API_KEY1")
api_key2 = os.getenv("API_KEY2")
api_key3 = os.getenv("API_KEY3")

api_keys=[api_key1,api_key2,api_key3]
api_cycle=cycle(api_keys)


freinds=['혜린핑', '고구마유스2','고구마유스1','노엉탁']

yesterday = date.today() - timedelta(days=1)


# 유저 이름 추출
def get_user_name(n):
    rank=[]
    user_name=[]
    for i in range(1,n):
        api_key = next(api_cycle)
        headers = {
        "Accept": "application/json",
        "x-nxopen-api-key": api_key
        }
        url=f'https://open.api.nexon.com/maplestory/v1/ranking/overall?date={yesterday}&page={i}'
        r=json.loads(requests.get(url, headers=headers).text)
        rank.append(r)

        print(rank)

    for j in range(len(rank)):
        user_name.extend([rank[j]['ranking'][i]['character_name'] for i in range(len(rank[j]['ranking']))])

    return user_name


#%%

user_name=get_user_name(10)

#데이터 추가
user_name=freinds+user_name


#%%
def get_ocid(user_name):
    ocid_user={}
    count=0

    for name in user_name:
        api_key=next(api_cycle)
        headers = {
        "Accept": "application/json",
        "x-nxopen-api-key": api_key
        }
        try:
            name_url=f'https://open.api.nexon.com/maplestory/v1/id?character_name={name}'
            data=json.loads(requests.get(name_url, headers=headers).text)
            ocid_user[data['ocid']]=name
            time.sleep(0.1)
        except:
            print(f"{name} 유저 ocid 검색 불가")
        count+=1
        if count%100==0:
            print(f"{count}만큼 ocid 추출 완료 | 진행률 : {count/len(user_name)}% ")

    return ocid_user


#ocid 추출
ocid_user = get_ocid(user_name)
with open('data/ocid_user.pickle', 'wb') as f:
    pickle.dump(ocid_user, f)



# ocid로 유저 캐시템 데이터 추출
def get_user_item(ocid_user):
    
    cashitem=[]
    count=0

    ocid=list(ocid_user.keys())

    for i in ocid:
        time.sleep(0.1)
        api_key=next(api_cycle)
        headers = {
        "Accept": "application/json",
        "x-nxopen-api-key": api_key
        }
        try:
            url=f'https://open.api.nexon.com/maplestory/v1/character/cashitem-equipment?ocid={i}'
            data=json.loads(requests.get(url, headers=headers).text)
            cashitem.append(data)
        except:
            pass
        count+=1
        if count%100==0:
            print(f"{count}번째 캐릭터 캐시템 추출 완료")

    return cashitem

cashitem=get_user_item(ocid_user)
with open('data/cashitem.pickle', 'wb') as f:
    pickle.dump(cashitem, f)



# 아이템 리스트, 유저 아이템 소지 목록 뽑기
def item_data(cashitem):

    total_item=set()
    user_item=[]

    #투명셋은 너무 많이 사용하기 때문에 추천에서 제거.
    except_list=['투명 장갑', '투명 안경', '투명 방패', '투명 블레이드', '투명 무기', '투명 모자', '투명 얼굴장식', '투명 아대', '투명 너클', '투명 귀고리', '투명 해골 장갑', '투명 망토', '투명 신발','경험치 부스트 링(15%)','혈맹의 반지']

    item_preset=['cash_item_equipment_base','cash_item_equipment_preset_1','cash_item_equipment_preset_2','cash_item_equipment_preset_3']

    for i in range(len(cashitem)):
        try:
            for p in item_preset:
                temp=[]
                for j in range(len(cashitem[i][p])):
                    if cashitem[i][p][j]['cash_item_name'] not in except_list:
                        temp.append(cashitem[i][p][j]['cash_item_name'])
                    else:
                        pass
                if not temp:
                    pass
                else:
                    user_item.append(temp)
                    total_item.update(temp)
        except:
            pass

    total_item=list(total_item)


    return user_item,total_item


user_item,total_item=item_data(cashitem)



# pickle 파일로 total_tiem, user_item 저장하기
with open('data/total_item.pickle', 'wb') as f:
    pickle.dump(total_item, f)

with open('data/user_item.pickle', 'wb') as f:
    pickle.dump(user_item, f)
# %%
