import os, pickle, numpy as np, pandas as pd
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import bm25_weight
from implicit.evaluation import train_test_split       
from itertools import product


os.environ.setdefault("OPENBLAS_NUM_THREADS", "1") # OpenBLAS 과다 쓰레드 경고 방지

#데이터 피벗
with open("data/total_item.pickle", "rb") as f:
    total_item = pickle.load(f)

with open("data/user_item.pickle", "rb") as f:
    user_item_raw = pickle.load(f)

df = pd.DataFrame({
    "user_name": list(user_item_raw.keys()),
    "items":     list(user_item_raw.values())
})

df  = df.explode("items")
df["preset"] = df.groupby("user_name").cumcount()
df  = df.explode("items")

pivot = (
    df.pivot_table(index=["user_name", "preset"],
                   columns="items",
                   aggfunc=lambda x: 1,
                   fill_value=0)
      .reset_index()
)
pivot_items = pivot.drop(columns=["user_name", "preset"])

#학습을 위해 희소 행렬 + 인기 아이템의 경우 가중치를 낮추기 위해 bm25 사용
rating_csr = bm25_weight(csr_matrix(pivot_items.values), K1=100, B=0.8)

#유저의 아이템 중 일부를 0으로 바꿔 추천 시스템이 이를 추천하는지 확인을 통해 시스템의 성능을 확인!
train_csr, valid_csr = train_test_split(rating_csr, train_percentage=0.8)

# Precision@K 를 통해 시스템의 성능을 확인
def precision_at_k_manual(model, train_mat, test_mat, K=20):

    scores = model.user_factors @ model.item_factors.T  #점수 행렬

    if scores.shape != train_mat.shape:
        scores = scores.T     

    seen = train_mat.tocsr()
    rows, cols = seen.nonzero()
    scores[rows, cols] = -np.inf
    indptr, indices = test_mat.indptr, test_mat.indices
    prec_sum, user_cnt = 0.0, test_mat.shape[0]

    for u in range(user_cnt):
        start, end = indptr[u], indptr[u+1]
        if start == end:
            continue                        # 숨겨둔 아이템이 없는 유저
        positives = indices[start:end]
        topk = np.argpartition(-scores[u], K)[:K]
        hit = np.intersect1d(positives, topk, assume_unique=True).size
        prec_sum += hit / K

    return prec_sum / user_cnt

# 하이퍼 파라미터 그리드 방식을 통해 설정
def grid_search(param_grid, train_mat, valid_mat, K=20):
    best, best_score, logs = None, -1, []

    for f, reg, a in product(param_grid["factors"],
                              param_grid["reg"],
                              param_grid["alpha"]):
        model = AlternatingLeastSquares(
            factors=f, regularization=reg,
            iterations=20, alpha=a, use_gpu=False
        )
        model.fit(train_mat.T)

        prec = precision_at_k_manual(model, train_mat, valid_mat, K)
        logs.append((f, reg, a, prec))

        if prec > best_score:
            best, best_score = (f, reg, a), prec

    return best, best_score, pd.DataFrame(
        logs, columns=["factors", "reg", "alpha", "prec@K"]
    )

param_grid = {
    "factors": [32,48,56,64],
    "reg":     [0.01,0.02,0.03, 0.05],
    "alpha":   [3,5,7]
}

best_params, best_prec, _ = grid_search(param_grid, train_csr, valid_csr, K=20) #val 값은 20으로 고정.
print(f"Best params = {best_params},  Precision@20 = {best_prec:.4f}")
