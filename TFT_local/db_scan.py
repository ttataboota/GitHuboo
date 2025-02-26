import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
import pandas as pd
import hdbscan
from scipy.sparse import csr_matrix

df = pd.read_csv("data/df_champ_usage.csv")
X = csr_matrix(df.values)

# HDBSCAN 진행!
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,  # 군집의 최소 크기
    min_samples=5,        # 코어 포인트가 되기 위한 최소 이웃 수
    metric='cosine'    # 거리 척도 (기본값은 유클리드 거리)
)
cluster_labels = clusterer.fit_predict(X)

# 라벨 저장
df['class'] = cluster_labels

print(f"클러스터 개수: {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)}")  # 군집 개수
print(f"노이즈 포인트 비율: {np.sum(cluster_labels == -1) / len(cluster_labels):.2%}")  # 노이즈 비율
