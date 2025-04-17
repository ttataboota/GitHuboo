#%%

import requests
import json
import pandas as pd
import time
from datetime import date
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
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

    for j in range(len(rank)):
        user_name.extend([rank[j]['ranking'][i]['character_name'] for i in range(len(rank[j]['ranking']))])

    return user_name

# 유저 이름 > ocid
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
            print(f"{count}만큼 ocid 추출 완료 | 진행률 : {round(count/len(user_name)*100,3)}% ")

    return ocid_user

# ocid > 유저 캐시템 데이터 추출
def get_user_item(ocid_user):
    
    cashitem={}
    count=0
    error_count=0

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
            name=ocid_user[i]
            cashitem[name]=data

        except:
            error_count+=1
            if error_count>100:
                print("오류 다수 발생. api 호출량 한계 도달 or 오류 있음 확인 요망.")
                break
            else:
                pass
        count+=1
        if count%100==0:
            print(f"{count}번째 캐릭터 캐시템 추출 완료")

    return cashitem

# 유저 보유 캐시 아이템 이름 추출
def item_data(cashitem):
    item_preset=['cash_item_equipment_base','cash_item_equipment_preset_1','cash_item_equipment_preset_2','cash_item_equipment_preset_3']
    except_item=['반지','투명','경험치 부스트 링(15%)']
    user_name=list(cashitem.keys())

    user_item={}
    total_item=set()


   
    for name in user_name:
        user_item_temp=[]
        
        for preset in item_preset:
            user_item_preset_temp=[]

            for data in cashitem[name][preset]:
                item_name=data['cash_item_name']
                if "반지" in item_name or "투명" in item_name:
                    continue
                else:
                    user_item_preset_temp.append(item_name)

            if not user_item_preset_temp:
                pass
            else:
                user_item_temp.append(user_item_preset_temp)
                total_item.update(user_item_preset_temp)

        user_item[name]=user_item_temp

    return user_item,total_item

# 유저 추가를 원할 경우 사용
def user_add(user_name):
    ocid_user={}
    api_key=next(api_cycle)
    headers = {
    "Accept": "application/json",
    "x-nxopen-api-key": api_key
    }
    try:
        name_url=f'https://open.api.nexon.com/maplestory/v1/id?character_name={user_name}'
        data=json.loads(requests.get(name_url, headers=headers).text)
        ocid_user[data['ocid']]=user_name
        time.sleep(0.1)
    except:
        print(f"{user_name} 유저 ocid 검색 불가")

    user_item_temp,total_item_temp=item_data(get_user_item(ocid_user))

    # 파일 불러오기
    with open('data/total_item.pickle', 'rb') as f:
        total_item = pickle.load(f)
    with open('data/user_item.pickle', 'rb') as f:
        user_item_raw = pickle.load(f)

    #파일 업데이트
    total_item=total_item|total_item_temp

    user_item_raw.update(user_item_temp)

    # total_tiem, user_item 업데이트 저장
    with open('data/total_item.pickle', 'wb') as f:
        pickle.dump(total_item, f)

    with open('data/user_item.pickle', 'wb') as f:
        pickle.dump(user_item_raw, f)


# %%

#초반 데이터 만들기
yesterday = date.today() - timedelta(days=1) # 데이터 추출은 코드 실행일 하루전으로 고정.
user_name=get_user_name(10) # 랭킹 상위 10페이지까지의 유저 추출
freinds=['혜린핑','고구마유스1','노엉탁','마조리카33','진븀']
user_name=freinds+user_name

#ocid 추출/저장
ocid_user = get_ocid(user_name)
with open('data/ocid_user.pickle', 'wb') as f:
    pickle.dump(ocid_user, f)

#cashitem 추출/저장
cashitem=get_user_item(ocid_user)
with open('data/cashitem.pickle', 'wb') as f:
    pickle.dump(cashitem, f)

# user_item,total_item 추출/저장
user_item,total_item=item_data(cashitem)
with open('data/total_item.pickle', 'wb') as f:
    pickle.dump(total_item, f)
with open('data/user_item.pickle', 'wb') as f:
    pickle.dump(user_item, f)

#%%
# 유저 추가해보기
user_add("열린자과")

# %%
