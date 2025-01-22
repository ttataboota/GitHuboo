import requests
import json
import pandas as pd
from pandas import json_normalize
import time
from itertools import cycle,zip_longest
import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


#챌린저 게임 불러오기
main_df = pd.read_feather('./challenger_game_Data.feather')
game_df=main_df.copy()

with open('./tft13-trait.json','r',encoding='utf-8') as json_file:
  data_dragon_trait=json.load(json_file)
with open('./tft13-champion.json','r',encoding='utf-8') as json_file:
  data_dragon_champion=json.load(json_file)
with open('./tft13-item.json','r',encoding='utf-8') as json_file:
  data_dragon_item=json.load(json_file)
with open('./tft13-augments.json','r',encoding='utf-8') as json_file:
  data_dragon_augments=json.load(json_file)

data_dragon=[data_dragon_trait,data_dragon_champion,data_dragon_item,data_dragon_augments]


#traits-특성 dic 만들기
df=pd.DataFrame(data_dragon_trait['data'])
df_eng_kor_traits=df.iloc[0:2,:]
dic_eng_kor_traits={df_eng_kor_traits.iloc[0,i] : df_eng_kor_traits.iloc[1,i] for i in range (df_eng_kor_traits.shape[1]) }

#champion-영웅 dic 만들기
df=pd.DataFrame(data_dragon_champion['data'])
df_eng_kor_champion=df.iloc[0:2,:]
dic_eng_kor_champion={df_eng_kor_champion.iloc[0,i] : df_eng_kor_champion.iloc[1,i] for i in range (df_eng_kor_champion.shape[1]) }

#item-아이템 dic 만들기
df=pd.DataFrame(data_dragon_item['data'])
df_eng_kor_item=df.iloc[0:2,:]
dic_eng_kor_item={df_eng_kor_item.iloc[0,i] : df_eng_kor_item.iloc[1,i] for i in range (df_eng_kor_item.shape[1]) }

#augments-특성 dic 만들기
df=pd.DataFrame(data_dragon_augments['data'])
df_eng_kor_augments=df.iloc[0:2,:]
dic_eng_kor_augments={df_eng_kor_augments.iloc[0,i] : df_eng_kor_augments.iloc[1,i] for i in range (df_eng_kor_augments.shape[1]) }


# 챔프 사용 여부 df 만들기

df_champ_usage=pd.DataFrame(columns=df_eng_kor_champion.columns)
for i in range(len(game_df['units'])):
  units=[]
  for j in range(len(game_df['units'][i])):
    units.append(game_df['units'][i][j]['character_id'])
  ithchamplist=[]
  for k in range(len(df_champ_usage.columns)):
    if df_champ_usage.columns[k] in units:
      ithchamplist.append(1)
    else:
      ithchamplist.append(0)
  df_champ_usage.loc[i]=ithchamplist




#pca 이용 차원 축소(6코 기물 걸러질 것으로 예상)
def pca_n(df_champ_usage):
  n_components = range(1, len(df_champ_usage.columns) + 1) 
  explained_variance_ratio = []

  for n in n_components:
      pca = PCA(n_components=n)
      pca.fit(df_champ_usage)
      explained_variance_ratio.append(np.sum(pca.explained_variance_ratio_))
  thresholds = [0.7, 0.8, 0.9]
  threshold_points = {}

  for threshold in thresholds:
      for i, variance in enumerate(explained_variance_ratio):
          if variance >= threshold:
              threshold_points[threshold] = (n_components[i], variance)
              break
  plt.figure(figsize=(10, 6))
  plt.plot(n_components, explained_variance_ratio, marker='o', label='Explained Variance Ratio')
  plt.xlabel('Number of Components')
  plt.ylabel('Explained Variance Ratio')
  plt.title('Scree Plot')


  for threshold, (num_components, variance) in threshold_points.items():
      plt.axvline(x=num_components, color='r', linestyle='--', alpha=0.7, label=f'Threshold {threshold}')
      plt.annotate(f'{threshold} ({num_components} components)', 
                  xy=(num_components, variance), 
                  xytext=(num_components + 0.5, variance - 0.05), 
                  arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10)

  plt.legend()
  plt.show()


pca_n(df_champ_usage)



