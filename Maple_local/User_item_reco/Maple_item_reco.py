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
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import pickle
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from implicit.als import AlternatingLeastSquares
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.preprocessing import OneHotEncoder
from sklearn.datasets import dump_svmlight_file
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# 파일 불러오기
with open('data/total_item.pickle', 'rb') as f:
    total_item = pickle.load(f)
with open('data/user_item.pickle', 'rb') as f:
    user_item_raw = pickle.load(f)

# 데이터 변환 
df = pd.DataFrame({
    'user_name': list(user_item_raw.keys()),
    'items': list(user_item_raw.values())
})

df_exploded = df.explode('items')
df_exploded['preset'] = df_exploded.groupby('user_name').cumcount()

df_exploded = df_exploded.explode('items')
pivot_df_raw = df_exploded.pivot_table(
    index=['user_name', 'preset'],   # 복합 인덱스: 유저 이름과 해당 프리셋 위치
    columns='items',                # 아이템 목록(여기서는 리스트가 아니라 미리 explode된 아이템명이어야 함)
    aggfunc=lambda x: 1,            # 해당 아이템이 있으면 1
    fill_value=0
)

pivot_df_name = pivot_df_raw.reset_index() #이중인덱스 제거
pivot_df = pivot_df_name.drop(columns=['user_name', 'preset']) #학습을 위해 나머지는 쳐내기

#%%
def reco_ALS(pivot_df,factors,regularization,iterations,alpha):
    #희소행렬 변환
    rating_matrix = csr_matrix(pivot_df)

    # ALS 모델 하이퍼 파라미터 수정 필요!
    als_model = AlternatingLeastSquares(factors=factors, regularization=regularization, iterations=iterations, alpha=alpha)
    als_model.fit(rating_matrix.T)  

    # 추천
    als_predictions = np.dot(als_model.item_factors, als_model.user_factors.T)

    return als_predictions


def user_item_reco(user_name,als_predictions):

    user_name_index = pivot_df_name[pivot_df_name['user_name'] == user_name].index.tolist()
    preset=0

    for user_index in user_name_index:
        recommended_items_index = np.argsort(-als_predictions[user_index,:])[:20]  # ALS가 예측한 상위 20개 아이템

        user_having_item=pivot_df.iloc[user_index][pivot_df.iloc[user_index]>0].keys()

        reco_item_als=[]
        for i in recommended_items_index:
            reco_item_als.append(pivot_df.keys()[i])

        reco_item=[item for item in reco_item_als if item not in user_having_item ]
        preset+=1
        print(f"프리셋 {preset}번 추천 아이템 : {reco_item}")

    return 0



als_predictions=reco_ALS(pivot_df,200,0.1,20,2)
user_item_reco("노엉탁",als_predictions)


#%%

# 유사도 기반 추천
def reco_Pearson(user_name):

    # 피어슨 상관계수 전체 계산 << 이거 써서 한번 계산해두고 나중에 하는건 서비스 할때 필요...지금은 하나씩 계산이 유용할듯
    # user_similarity = df.T.corr(method='pearson')
    user_name_index = pivot_df_name[pivot_df_name['user_name'] == user_name].index.tolist()

    preset=0

    for user in user_name_index:
        my_vector = pivot_df.iloc[user]

        similarities = {}

        for other_id in pivot_df.index:
            if other_id != user:
                other_vector = pivot_df.loc[other_id]
                correlation, _ = pearsonr(my_vector, other_vector)
                if correlation>0:
                    similarities[other_id] = correlation

        

        # 유저가 소지하지 않은 아이템 필터링
        user_items = pivot_df.iloc[user]
        non_owned_items = user_items[user_items == 0].index

        # 추천 점수 계산
        scores = {}
        for item in non_owned_items:
            item_scores = pivot_df.loc[list(similarities.keys()), item] * np.array(list(similarities.values()))
            scores[item] = item_scores.sum() / np.array(list(similarities.values())).sum()

        # 상위 20개의 아이템 추천
        recommended_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
        preset+=1
        print(f"프리셋 {preset}번 추천 아이템 : {[item[0] for item in recommended_items]}")

    return 0


reco_Pearson("고구마유스1")


def reco_Pearson(user_name):

    # 피어슨 상관계수 전체 계산 << 이거 써서 한번 계산해두고 나중에 하는건 서비스 할때 필요...지금은 하나씩 계산이 유용할듯
    # user_similarity = df.T.corr(method='pearson')
    user_name_index = pivot_df_name[pivot_df_name['user_name'] == user_name].index.tolist()

    preset=0

    for user in user_name_index:
        my_vector = pivot_df.iloc[user]

        similarities = {}

        for other_id in pivot_df.index:
            if other_id != user:
                other_vector = pivot_df.loc[other_id]
                correlation, _ = pearsonr(my_vector, other_vector)
                if correlation>0:
                    similarities[other_id] = correlation

        

        # 유저가 소지하지 않은 아이템 필터링
        user_items = pivot_df.iloc[user]
        non_owned_items = user_items[user_items == 0].index

        # 추천 점수 계산
        scores = {}
        for item in non_owned_items:
            item_scores = pivot_df.loc[list(similarities.keys()), item] * np.array(list(similarities.values()))
            scores[item] = item_scores.sum() / np.array(list(similarities.values())).sum()

        # 상위 20개의 아이템 추천
        recommended_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
        preset+=1
        print(f"프리셋 {preset}번 추천 아이템 : {[item[0] for item in recommended_items]}")

    return 0



# def reco_FM(group_id, pivot_df):

#     df = pivot_df.copy()
#     df = df.reset_index().melt(id_vars=['group_id'], var_name='item', value_name='owned')
#     df = df[df['owned'] == 1]  # 소지한 아이템만 유지

#     # 데이터 변환
#     df['group_id'] = df['group_id'].astype(str)
#     df['item'] = df['item'].astype(str)

#     # 훈련/테스트 데이터 분할
#     train, test = train_test_split(df, test_size=0.2, random_state=42)

#     v = DictVectorizer()
#     X_train = v.fit_transform(train[['group_id', 'item']].to_dict(orient='records'))
#     X_test = v.transform(test[['group_id', 'item']].to_dict(orient='records'))

#     y_train = np.ones(len(train))
#     y_test = np.ones(len(test))

#     # 모델 하이퍼 파라미터
#     fm = pylibfm.FM(num_factors=8, task="classification", initial_learning_rate=0.01, num_iter=10, verbose=True)
#     fm.fit(X_train, y_train)


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


#     y_pred = []
#     with open('reco_output.txt') as f:
#         for line in f:
#             y_pred.append(float(line.strip()))
    

#     recommended_items = sorted(zip(items, y_pred), key=lambda x: x[1], reverse=True)[:20]
    
#     return recommended_items


# FM_reco=reco_FM(0,pivot_df)

# %%
