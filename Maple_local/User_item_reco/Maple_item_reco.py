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
from implicit.als import AlternatingLeastSquares



# 파일 불러오기
with open('data/total_item2.pickle', 'rb') as f:
    total_item = pickle.load(f)
with open('data/user_item2.pickle', 'rb') as f:
    user_item = pickle.load(f)


# 데이터 변환 

df = pd.DataFrame({'group_id': range(len(user_item)), 'items': user_item})
df_exploded = df.explode('items')
pivot_df = df_exploded.pivot_table(index='group_id', columns='items', aggfunc=lambda x: 1, fill_value=0)


#희소행렬 변환
rating_matrix = csr_matrix(pivot_df)



# ALS 모델 하이퍼 파라미터 수정 필요!
als_model = AlternatingLeastSquares(factors=100, regularization=0.01, iterations=50)
als_model.fit(rating_matrix.T)  

# 추천
als_predictions = np.dot(als_model.item_factors, als_model.user_factors.T)



# 유저 인덱스
user_index = 2



recommended_items_index = np.argsort(-als_predictions[user_index,:])[:20]  # ALS가 예측한 상위 20개 아이템

user_having_item=pivot_df.iloc[user_index][pivot_df.iloc[user_index]>0].keys()

reco_item_als=[]
for i in recommended_items_index:
    reco_item_als.append(pivot_df.keys()[i])

reco_item=[item for item in reco_item_als if item not in user_having_item ]


reco_item

# %%
