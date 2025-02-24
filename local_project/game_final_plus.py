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


#게임 불러오기 새 데이터 나올시 수정!
main_df = pd.read_feather('./challenger_game_Data.feather')
game_df=main_df.copy()


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




# 챔프 사용 여부 df 만들기
champ_list = list(dic_eng_kor["champion"].keys())
df_champ_usage = pd.DataFrame(
    0,
    index=range(len(game_df)),
    columns=champ_list
)
# 0으로 채우고 사용한 챔프 1로 바꾸기
for i, units_info in enumerate(game_df['units']):
    used_champs = [unit['character_id'] for unit in units_info if unit['character_id'] in champ_list ]
    # 사용된 챔피언에만 1로 표시
    for champ in used_champs:
        df_champ_usage.loc[i, champ] = 1




#자동 pca 이후 kmean 까지
def auto_pca_kmean(optimal_k,df_champ_usage):
  pca = PCA(n_components=0.95, random_state=42)
  pca_champ_usage=pca.fit_transform(df_champ_usage)  #95퍼센트 데이터로 pca 진행
  
  kmeans = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=300, n_init=10, random_state=0)
  pca_champ_kmean = kmeans.fit(pca_champ_usage)

  df_champ_usage['class']=pca_champ_kmean.labels_

  return 0


slope_data=[]
for i in range(10,60):
    auto_pca_kmean(i,df_champ_usage)
    class_champ_usage=df_champ_usage.groupby('class').sum()
    sorted_class_champ_usage = class_champ_usage.apply(lambda row: row.sort_values(ascending=False).values, axis=1)
    slope=0
    for class_label, values in sorted_class_champ_usage.items():
        slope+=(int(values[3])-int(values[0]))/4
    slope_data.append(slope/i)

plt.plot(range(10,60),slope_data)

from kneed import KneeLocator

kneedle = KneeLocator(range(10,60), slope_data, curve="concave", direction="increasing")
knee_point = kneedle.knee

print(knee_point)

plt.show()


    