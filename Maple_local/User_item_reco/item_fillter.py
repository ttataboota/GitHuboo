#%%
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
from scipy.sparse import csr_matrix
import pickle


# 파일 불러오기
with open('data/total_item.pickle', 'rb') as f:
    total_item = pickle.load(f)
with open('data/user_item.pickle', 'rb') as f:
    user_item = pickle.load(f)
with open('data/cashitem.pickle', 'rb') as f:
    cashitem = pickle.load(f)


#%%
filtered_words = [word for word in total_item if word.endswith("반지")]


# 아이템 리스트, 유저 아이템 소지 목록 뽑기
def item_data(cashitem):

    total_item=set()
    user_item=[]

    #투명셋은 너무 많이 사용하기 때문에 추천에서 제거. + 반지류 제거
    except_list=['투명 장갑', '투명 안경', '투명 방패', '투명 블레이드', '투명 무기', '투명 모자', '투명 얼굴장식', '투명 아대', '투명 너클', '투명 귀고리', '투명 해골 장갑', '투명 망토', '투명 신발','경험치 부스트 링(15%)','혈맹의 반지']
    except_list=except_list+filtered_words
    
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
with open('data/total_item2.pickle', 'wb') as f:
    pickle.dump(total_item, f)

with open('data/user_item2.pickle', 'wb') as f:
    pickle.dump(user_item, f)