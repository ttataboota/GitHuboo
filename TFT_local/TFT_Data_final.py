
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
from sklearn.metrics import silhouette_samples, silhouette_score
from kneed import KneeLocator


#게임 불러오기 새 데이터 나올시 수정!
main_df = pd.read_feather('data/master_game_Data.feather')
game_df=main_df.copy()


class Data_Dragon:
    def __init__(self,now_season):
      self.now_season=now_season
      self.json_files= {
        "trait": "tft-trait.json",
        "champion": "tft-champion.json",
        "item": "tft-item.json",
        "augments": "tft-augments.json"
        }
      self.data_dragon = {}
      self.dic_eng_kor = {}
      
    def load_data(self):
      for key, filename in self.json_files.items():
        with open(f"data/{filename}", 'r', encoding='utf-8') as json_file:
            self.data_dragon[key] = json.load(json_file)

    def gen_dic_eng_kor(self):
      for key, data in self.data_dragon.items():
        df = pd.DataFrame(data['data'])  
        df_eng_kor = df.iloc[0:2, :]  # 영어-한국어 매핑
        dic_temp = {df_eng_kor.iloc[0, i]: df_eng_kor.iloc[1, i] for i in range(df_eng_kor.shape[1])} 
        if key=='item':
          self.dic_eng_kor[key] = {k: v for k, v in dic_temp.items()}  # item 은 시즌 지나도 재활용해서 시즌필터링 x
        else:
          self.dic_eng_kor[key] = {k: v for k, v in dic_temp.items() if f'TFT{self.now_season}' in k}  # 시즌 필터링
      
      
    def get_dic_eng_kor(self):
        return self.dic_eng_kor
    

#한번에 실행하기
def get_Data_Dragon(season):
  tft_data=Data_Dragon(season) # 시즌 13 데이터 생성
  tft_data.load_data() # 시즌 13 데이터만 불러오기
  tft_data.gen_dic_eng_kor() # 시즌 13 딕셔너리 만들기
  dic_eng_kor=tft_data.get_dic_eng_kor() #시즌 13 딕셔너리 불러오기
  return dic_eng_kor





class User_df:

  def __init__(self,game_df,dic_eng_kor):
    self.game_df=game_df
    self.dic_eng_kor=dic_eng_kor  
    self.df_champ_usage = None  
    self.df_item_champ_usage = None     

  def gen_df_champ_usage(self):
    # 챔프 사용 여부 df 만들기
    champ_list = list(self.dic_eng_kor["champion"].keys())
    self.df_champ_usage = pd.DataFrame(
        0,
        index=range(len(self.game_df)),
        columns=champ_list
    )
    # 0으로 채우고 사용한 챔프 1로 바꾸기
    for i, units_info in enumerate(self.game_df['units']):
        used_champs = [unit['character_id'] for unit in units_info if unit['character_id'] in champ_list ]
        # 사용된 챔피언에만 1로 표시
        for champ in used_champs:
            self.df_champ_usage.loc[i, champ] = 1
    
    self.df_champ_usage=self.df_champ_usage.rename(columns=self.dic_eng_kor['champion'])

  def get_df_champ_usage(self):
     return self.df_champ_usage
    
  def gen_df_item_champ_usage(self):
    #챔프별 아이템 df 만들기
    champ_list = list(self.dic_eng_kor['champion'].keys())
    item_list=list(self.dic_eng_kor['item'].keys())

    self.df_item_champ_usage = pd.DataFrame(
        0,
        index=champ_list,
        columns=item_list
        )
    for units_info in self.game_df['units']:
      for unit in units_info:
        if unit['character_id'] in champ_list:
          for item in unit['itemNames']:
            self.df_item_champ_usage.loc[unit['character_id'], item] += 1

    self.df_item_champ_usage=self.df_item_champ_usage.loc[:, self.df_item_champ_usage.sum() != 0]

    self.df_item_champ_usage=self.df_item_champ_usage.rename(
        index=self.dic_eng_kor['champion'],  # 행 이름 변경
        columns=self.dic_eng_kor['item']  # 열 이름 변경 
        )
  
  def get_df_item_champ_usage(self):
     return self.df_item_champ_usage


#한번에 얻기
def get_User_df(game_df,season):
  make_user_df=User_df(game_df,get_Data_Dragon(season)) # 유저 플레이 데이터로 챔피언, 아이템 사용 df 만들기
  make_user_df.gen_df_champ_usage() # 챔피언 사용 df 만들기
  make_user_df.gen_df_item_champ_usage() # 챔피언별 사용 아이템 df 만들기
  df_champ_usage=make_user_df.get_df_champ_usage()
  df_item_champ_usage=make_user_df.get_df_item_champ_usage()
  return {'champ': df_champ_usage, 'item': df_item_champ_usage}

class DA:
  def __init__(self,game_df,df_champ_usage,df_item_champ_usage):
     
    self.df_champ_usage=df_champ_usage
    self.df_item_champ_usage=df_item_champ_usage
    self.game_df=game_df
     
  def get_game_df(self):
     return self.game_df
  
  def get_df_champ_usage(self):
    return self.df_champ_usage

  def get_df_item_champ_usage(self):
    return self.df_item_champ_usage



  #기본적 통계 확인
  def main_traits(self):
      
    #주요 특성 뽑기
    main_traits=[]
    sub=[]
    for i in range(len(self.game_df['traits'])):
      sub=[]
      for j in range(len(self.game_df['traits'][i])):
        traits=self.game_df['traits'][i][j]
        if traits['style']>=2:
          sub.append(traits['name'])
      main_traits.append(sub)

    #주요특성 df에 반영
    self.game_df['main_traits']=main_traits

    #특성별 평균,분산
    traits_stat = []

    for i in range(len(self.game_df['main_traits'])):
        for j in range(len(self.game_df['main_traits'][i])):
            traits_stat.append({'trait': self.game_df['main_traits'][i][j], 'placement': self.game_df['placement'][i]})
    traits_stat=pd.DataFrame(traits_stat).groupby('trait').agg({'placement': ['mean', 'var']}).sort_values(by=('placement','mean'))
    traits_stat.index=traits_stat.index.map(self.dic_eng_kor["trait"])

    return traits_stat #가장 단순한 통계


  #자동 pca 이후 kmean 까지
  def auto_pca_kmean(self):
    pca = PCA(n_components=0.95, random_state=42)
    pca_champ_usage=pca.fit_transform(self.df_champ_usage)  #95퍼센트 데이터로 pca 진행

    #실루엣으로 자동 k 값 설정
    k_values = range(10, 30) #챌린저 데이터에선 18이 최고 결과 보여줘서 이 구간안에서 진행하면 적당할듯
    silhouette_scores = []

    for k in k_values:
      kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
      labels = kmeans.fit_predict(pca_champ_usage)
      score = silhouette_score(pca_champ_usage, labels)
      silhouette_scores.append(score)

    optimal_k = k_values[np.argmax(silhouette_scores)]
    silhouette_data=[k_values,silhouette_scores]

    kmeans = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=300, n_init=10, random_state=0)
    pca_champ_kmean = kmeans.fit(pca_champ_usage)

    self.df_champ_usage['class']=pca_champ_kmean.labels_
    self.game_df['class']=pca_champ_kmean.labels_
    # self.df_champ_usage.columns = self.df_champ_usage.columns.map(lambda col: self.dic_eng_kor['champion'].get(col, col))
    self.df_champ_usage['placement']=self.game_df['placement']



    print(f"silhouette_scores 이용. {optimal_k}가 가장 적절한 k값으로 예상")

    return silhouette_data



  # 실루엣 결과가 마음에 안든다! 새로운 k값을 얻을 기준이 필요
  # k 값에 따른 kmean 필요
  def k_kmean(self,k):
    pca = PCA(n_components=0.95, random_state=42)
    pca_champ_usage=pca.fit_transform(self.df_champ_usage)  #95퍼센트 데이터로 pca 진행

    kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=0)
    pca_champ_kmean = kmeans.fit(pca_champ_usage)
    self.df_champ_usage['class']=pca_champ_kmean.labels_
    


  def four_slope(self):
    slope_data=[]
    for i in range(10,60):
        self.k_kmean(i)
        class_champ_usage=self.df_champ_usage.groupby('class').sum()
        sorted_class_champ_usage = class_champ_usage.apply(lambda row: row.sort_values(ascending=False).values, axis=1)
        slope=0
        for class_label, values in sorted_class_champ_usage.items():
            slope+=(int(values[3])-int(values[0]))/4
        slope_data.append(slope/i)

    plt.plot(range(10,60),slope_data) # 가장 사용량 많은 4개의 챔피언의 사용량을 기준으로 기울기 측정

    #덱 분류가 잘되면 같은 챔피언을 기용하는 케이스 증가==기울기가 평탄해짐
    kneedle = KneeLocator(range(10,60), slope_data, curve="concave", direction="increasing")
    knee_point = kneedle.knee
    plt.show()

    self.k_kmean(knee_point)

    self.df_champ_usage['placement']=self.game_df['placement']
    print(f"slope 이용. {knee_point} 가 적절한 k 값으로 예상")



season13_user_df=get_User_df(game_df,13) #시즌 13 유저데이터 생성
print("1")
Data_An=DA(game_df,season13_user_df['champ'],season13_user_df['item']) # 유저데이터 분석 준비
print("2")
# slope_data=Data_An.four_slope() # 기울기 데이터로 k 값 생성 후 클래스 구분
Data_An.auto_pca_kmean()



df_champ_usage=Data_An.get_df_champ_usage()
df_item_champ_usage=Data_An.get_df_item_champ_usage()
game_df=Data_An.get_game_df()



# df_item_champ_usage.to_csv("data/slope_df_item_champ_usage.csv", index=True, encoding="utf-8-sig")
# df_champ_usage.to_csv("data/slope_df_champ_usage.csv", index=False, encoding="utf-8-sig")
# game_df.to_csv("data/slope_game_df.csv", index=False, encoding="utf-8-sig")

df_item_champ_usage.to_csv("data/sil_df_item_champ_usage.csv", index=True, encoding="utf-8-sig")
df_champ_usage.to_csv("data/sil_df_champ_usage.csv", index=False, encoding="utf-8-sig")
game_df.to_csv("data/sil_game_df.csv", index=False, encoding="utf-8-sig")

class Visual_data:
  def __init__(self,df_champ_usage,df_item_champ_usage,dic_eng_kor):

    self.df_item_champ_usage=df_item_champ_usage
    self.df_champ_usage=df_champ_usage
    self.dic_eng_kor=dic_eng_kor
    
      
  # 챔프 사용 빈도순 아이템 상위 25개 검색    
  def champ_item(self,champ):
    return self.df_item_champ_usage.loc[champ,:].sort_values(ascending=False).head(25)


  # n번째 덱 확인(등수 관련 없음)
  def n_deck(self,n):
    deck=self.df_champ_usage.groupby('class').sum()
    deck.rename(columns=self.dic_eng_kor["champion"], inplace=True)
    return deck.iloc[n,:].sort_values(ascending=False)

  # 덱 등수 확인
  def deck_rank(self):
    return self.game_df.groupby('class').agg({'placement': ['mean', 'var']}).sort_values(by=('placement','mean'))


  # n등 덱 확인
  def n_th_rank_deck(self,n):
      n_rank=self.n_deck(self.deck_rank().index[n-1])
      return n_rank


  # 자동 pca, kmean 이후에 덱 구성(기물 10개 까지 정리 이후 등수대로 정리)

  # def final_data(self):
  #     optimal_k=auto_pca_kmean(self.df_champ_usage)
  #     final_data=pd.DataFrame()  
  #     for i in range(optimal_k):
  #         final_data = pd.concat([final_data, pd.DataFrame([self.n_th_rank_deck(i).head(10).index])], ignore_index=True)
  #     return final_data