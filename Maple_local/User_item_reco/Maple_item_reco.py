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
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.preprocessing import OneHotEncoder
from sklearn.datasets import dump_svmlight_file
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
# from pyfm import pylibfm
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split



# 파일 불러오기
with open('data/total_item2.pickle', 'rb') as f:
    total_item = pickle.load(f)
with open('data/user_item2.pickle', 'rb') as f:
    user_item = pickle.load(f)


# 데이터 변환 

df = pd.DataFrame({'group_id': range(len(user_item)), 'items': user_item})
df_exploded = df.explode('items')
pivot_df = df_exploded.pivot_table(index='group_id', columns='items', aggfunc=lambda x: 1, fill_value=0)


def reco_ALS(pivot_df,factors,regularization,iterations,alpha):
    #희소행렬 변환
    rating_matrix = csr_matrix(pivot_df)

    # ALS 모델 하이퍼 파라미터 수정 필요!
    als_model = AlternatingLeastSquares(factors=factors, regularization=regularization, iterations=iterations, alpha=alpha)
    als_model.fit(rating_matrix.T)  

    # 추천
    als_predictions = np.dot(als_model.item_factors, als_model.user_factors.T)

    return als_predictions






def user_item_reco(user_index,als_predictions):

    recommended_items_index = np.argsort(-als_predictions[user_index,:])[:20]  # ALS가 예측한 상위 20개 아이템

    user_having_item=pivot_df.iloc[user_index][pivot_df.iloc[user_index]>0].keys()

    reco_item_als=[]
    for i in recommended_items_index:
        reco_item_als.append(pivot_df.keys()[i])

    reco_item=[item for item in reco_item_als if item not in user_having_item ]


    return reco_item



als_predictions=reco_ALS(pivot_df,60,0.1,20,4)
als_reco=user_item_reco(0,als_predictions)




# 유사도 기반 추천
def reco_Pearson(user, df):

    # # 피어슨 상관계수 계산
    # user_similarity = df.T.corr(method='pearson')


    my_vector = pivot_df.loc[user]

    similarities = {}

    for other_id in pivot_df.index:
        if other_id != user:
            other_vector = pivot_df.loc[other_id]
            correlation, _ = pearsonr(my_vector, other_vector)
            if correlation>0:
                similarities[other_id] = correlation

    

    # 유저가 소지하지 않은 아이템 필터링
    user_items = df.iloc[user]
    non_owned_items = user_items[user_items == 0].index

    # 추천 점수 계산
    scores = {}
    for item in non_owned_items:
        item_scores = df.loc[list(similarities.keys()), item] * np.array(list(similarities.values()))
        scores[item] = item_scores.sum() / np.array(list(similarities.values())).sum()

    # 상위 N개의 아이템 추천
    recommended_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
    return [item[0] for item in recommended_items]

pearson_reco=reco_Pearson(0,pivot_df)


# def reco_FM(group_id, pivot_df):

#     df = pivot_df.copy()
#     df = df.reset_index().melt(id_vars=['group_id'], var_name='item', value_name='owned')
#     df = df[df['owned'] == 1]  # 소지한 아이템만 유지

#     # 📌 데이터 변환
#     df['group_id'] = df['group_id'].astype(str)
#     df['item'] = df['item'].astype(str)

#     # 📌 훈련/테스트 데이터 분할
#     train, test = train_test_split(df, test_size=0.2, random_state=42)

#     # 📌 특성 벡터화 (One-Hot Encoding)
#     v = DictVectorizer()
#     X_train = v.fit_transform(train[['group_id', 'item']].to_dict(orient='records'))
#     X_test = v.transform(test[['group_id', 'item']].to_dict(orient='records'))

#     y_train = np.ones(len(train))
#     y_test = np.ones(len(test))

#     # 📌 FM 모델 학습
#     fm = pylibfm.FM(num_factors=8, task="classification", initial_learning_rate=0.01, num_iter=10, verbose=True)
#     fm.fit(X_train, y_train)

#     # 📌 예측
#     y_pred = fm.predict(X_test)
#     y_pred_binary = [1 if p > 0.5 else 0 for p in y_pred]
#     acc = accuracy_score(y_test, y_pred_binary)
#     print(f'Accuracy: {acc}')


#     items = list(pivot_df.columns)
#     test_data = pd.DataFrame({'group_id': [group_id] * len(items), 'item': items})
#     X_test = encoder.transform(test_data)
    
#     # 예측 수행
#     dump_svmlight_file(X_test, np.zeros(len(items)), 'reco_test.libsvm')
#     fm_model.setTest('reco_test.libsvm')
#     fm_model.predict('model.out', 'reco_output.txt')

#     # 결과 로드 및 정렬
#     y_pred = []
#     with open('reco_output.txt') as f:
#         for line in f:
#             y_pred.append(float(line.strip()))
    
#     # 추천 아이템 정렬
#     recommended_items = sorted(zip(items, y_pred), key=lambda x: x[1], reverse=True)[:20]
    
#     return recommended_items


# FM_reco=reco_FM(0,pivot_df)

# %%
