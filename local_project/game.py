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

#현 시즌
now_season=13

#traits-특성 dic 만들기
df=pd.DataFrame(data_dragon_trait['data'])
df_eng_kor_traits=df.iloc[0:2,:]
dic_eng_kor_traits={df_eng_kor_traits.iloc[0,i] : df_eng_kor_traits.iloc[1,i] for i in range (df_eng_kor_traits.shape[1]) }
dic_eng_kor_traits = {key: value for key, value in dic_eng_kor_traits.items() if f'TFT{now_season}' in key}

#champion-영웅 dic 만들기
df=pd.DataFrame(data_dragon_champion['data'])
df_eng_kor_champion=df.iloc[0:2,:]
dic_eng_kor_champion={df_eng_kor_champion.iloc[0,i] : df_eng_kor_champion.iloc[1,i] for i in range (df_eng_kor_champion.shape[1]) }
dic_eng_kor_champion = {key: value for key, value in dic_eng_kor_champion.items() if f'TFT{now_season}' in key}


#item-아이템 dic 만들기
df=pd.DataFrame(data_dragon_item['data'])
df_eng_kor_item=df.iloc[0:2,:]
dic_eng_kor_item={df_eng_kor_item.iloc[0,i] : df_eng_kor_item.iloc[1,i] for i in range (df_eng_kor_item.shape[1]) }
dic_eng_kor_item = {key: value for key, value in dic_eng_kor_item.items() if f'TFT{now_season}' in key}

#augments-특성 dic 만들기
df=pd.DataFrame(data_dragon_augments['data'])
df_eng_kor_augments=df.iloc[0:2,:]
dic_eng_kor_augments={df_eng_kor_augments.iloc[0,i] : df_eng_kor_augments.iloc[1,i] for i in range (df_eng_kor_augments.shape[1]) }
dic_eng_kor_augments = {key: value for key, value in dic_eng_kor_augments.items() if f'TFT{now_season}' in key}


# 챔프 사용 여부 df 만들기

df_champ_usage=pd.DataFrame(columns=list(dic_eng_kor_champion.keys()))  
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




#기본적 통계 확인
def main_traits(game_df):
    
  #주요 특성 뽑기
  main_traits=[]
  sub=[]
  for i in range(len(game_df['traits'])):
    sub=[]
    for j in range(len(game_df['traits'][i])):
      traits=game_df['traits'][i][j]
      if traits['style']>=2:
        sub.append(traits['name'])
    main_traits.append(sub)

  #주요특성 df에 반영
  game_df['main_traits']=main_traits


  #특성별 평균,분산
  traits_stat = []

  for i in range(len(game_df['main_traits'])):
      for j in range(len(game_df['main_traits'][i])):
          traits_stat.append({'trait': game_df['main_traits'][i][j], 'placement': game_df['placement'][i]})
  traits_stat=pd.DataFrame(traits_stat).groupby('trait').agg({'placement': ['mean', 'var']}).sort_values(by=('placement','mean'))
  traits_stat.index=traits_stat.index.map(dic_eng_kor_traits)

  return traits_stat # 이거 결과값도 저장하는쪽으로 가면 좋을듯?




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




def pca_kmean_cluster(n,df_champ_usage):
  pca = PCA(n_components=n)
  pca.fit(df_champ_usage)
  pca_champ_usage=pca.transform(df_champ_usage)

  wcss = []
  for i in range(10,40):
      kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
      kmeans.fit(pca_champ_usage)
      wcss.append(kmeans.inertia_)

  plt.plot(range(10, 40), wcss)
  plt.show()


def only_kmean_n(df_champ_usage):
  wcss = []
  for i in range(10,40):
      kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
      kmeans.fit(df_champ_usage)
      wcss.append(kmeans.inertia_)
  plt.plot(range(10, 40), wcss)
  plt.show()

def pca_95_kmean(k,df_champ_usage):
  pca = PCA(n_components=0.95, random_state=42)
  pca.fit_transform(df_champ_usage)
  pca.fit(df_champ_usage)
  pca_champ_usage=pca.transform(df_champ_usage)
  kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=0)
  pca_champ_kmean = kmeans.fit(pca_champ_usage)

  df_champ_usage['class']=pca_champ_kmean.labels_
  game_df['class']=pca_champ_kmean.labels_

  deck=df_champ_usage.groupby('class').sum()
  return deck

def pca_kmean(p,k,df_champ_usage):
  pca = PCA(n_components=p)
  pca.fit(df_champ_usage)
  pca_champ_usage=pca.transform(df_champ_usage)
  kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=0)
  pca_champ_kmean = kmeans.fit(pca_champ_usage)

  df_champ_usage['class']=pca_champ_kmean.labels_
  game_df['class']=pca_champ_kmean.labels_

  deck=df_champ_usage.groupby('class').sum()
  return deck



def deck_maker(deck,n):

  deck.rename(columns=dic_eng_kor_champion, inplace=True)
  return deck.iloc[n,:].sort_values(ascending=False)



def deck_rank(game_df):
   return game_df.groupby('class').agg({'placement': ['mean', 'var']}).sort_values(by=('placement','mean'))
   



