#%%
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from scipy.sparse import csr_matrix
import pickle
from implicit.als import AlternatingLeastSquares
from scipy.stats import pearsonr


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
    index=['user_name', 'preset'],  # 복합 인덱스: 유저 이름과 해당 프리셋 위치
    columns='items',   # 아이템 목록(여기서는 리스트가 아니라 미리 explode된 아이템명이어야 함)
    aggfunc=lambda x: 1,   # 해당 아이템이 있으면 1
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


als_predictions=reco_ALS(pivot_df,56,0.05,20,7)
user_item_reco("고구마유스1",als_predictions)


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


reco_Pearson("고구마유스1")

#%%

import numpy as np
from numpy.linalg import norm     # 코사인 유사도 계산용

def reco_cosine(user_name, pivot_df, pivot_df_name, top_k=20, eps=1e-9):
    """
    • user_name : 추천을 받을 대상 유저 ID
    • pivot_df  : 행 = 유저, 열 = 아이템(0/1 또는 평점)인 피벗 테이블
    • pivot_df_name : 'user_name' 컬럼이 있는 DataFrame (pivot_df와 인덱스 맞춰둠)
    • top_k     : 아이템 추천 개수
    • eps       : 0 벡터 divide-by-zero 방지용 작은 값
    """
    # 대상 유저의 행 인덱스 찾기
    user_idx_list = pivot_df_name[pivot_df_name['user_name'] == user_name].index.tolist()

    preset = 0
    for user_idx in user_idx_list:
        target_vec = pivot_df.iloc[user_idx].values
        similarities = {}

        # (1) 다른 유저들과 코사인 유사도 계산
        for other_idx in pivot_df.index:
            if other_idx == user_idx:
                continue

            other_vec = pivot_df.iloc[other_idx].values
            # --- 코사인 유사도 ---
            denom = (norm(target_vec) * norm(other_vec)) + eps
            if denom == 0:                 # 두 벡터 모두 0인 경우
                continue
            cosine_sim = np.dot(target_vec, other_vec) / denom
            if cosine_sim > 0:
                similarities[other_idx] = cosine_sim

        if not similarities:              # 양의 유사도인 이웃이 없으면 패스
            print(f"[경고] '{user_name}'와 유사한 유저를 찾지 못했습니다.")
            continue

        # (2) 아직 보유하지 않은 아이템 목록
        non_owned_items = target_vec == 0
        candidate_items = pivot_df.columns[non_owned_items]

        # (3) 아이템별 가중 점수 산출
        scores = {}
        sim_users = list(similarities.keys())
        sim_values = np.array(list(similarities.values()))

        # pivot_df.loc[sim_users, candidate_items]  →  (num_sim_users × num_items)
        weighted_matrix = pivot_df.loc[sim_users, candidate_items].values * sim_values[:, None]
        # 분자: 유사도 가중 합,  분모: 유사도 합
        item_scores = weighted_matrix.sum(axis=0) / (sim_values.sum() + eps)
        scores = dict(zip(candidate_items, item_scores))

        # (4) 상위 N개 추천
        recommended_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        preset += 1
        print(f"프리셋 {preset}번 추천 아이템 :", [item for item, _ in recommended_items])




# %%
