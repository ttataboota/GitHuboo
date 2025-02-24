#%%


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns




df=pd.read_csv("user_data_merged.csv",encoding="utf-8-sig")

def iso_forest():
    # 예: df['damage'], df['zloa']가 존재한다고 가정
    X = df[['user_damage', 'user_zloa_score']].values

    # IsolationForest 모델 생성
    # contamination은 이상치 비율(대략 추정)
    iso_forest = IsolationForest(contamination=0.2, random_state=42)
    iso_forest.fit(X)
    labels = iso_forest.predict(X)

    # -1: 이상치, 1: 정상치
    df['is_outlier'] = labels

    inliers = df[df['is_outlier'] == 1]
    outliers = df[df['is_outlier'] == -1]

    # 시각화
    plt.figure(figsize=(8,6))
    plt.scatter(inliers['user_damage'], inliers['user_zloa_score'],
                c='blue', alpha=0.5, label='Inliers')
    plt.scatter(outliers['user_damage'], outliers['user_zloa_score'],
                c='red', marker='x', label='Outliers')
    plt.title("IsolationForest Outlier Detection")
    plt.xlabel("Damage")
    plt.ylabel("ZLOA")
    plt.legend()
    plt.show()

# # 이상치 제거
# df_cleaned = df[df['is_outlier'] == 1]

def draw_scattering():
    x_values = df['user_damage']
    y_values = df['user_zloa_score']

    # Scatter plot 그리기
    plt.figure(figsize=(8, 6))
    plt.scatter(x_values, y_values, alpha=0.7, edgecolors='k')

    # 그래프 스타일
    plt.xlabel('Damage Data')
    plt.ylabel('ZLOA Data')

    plt.show()

def kmean_2():
    X = df[['user_damage', 'user_zloa_score']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means 모델 (클러스터 2개)
    kmeans = KMeans(n_clusters=2, random_state=42,init='k-means++')
    kmeans.fit(X_scaled)

    # 예측(할당)된 클러스터 라벨
    labels = kmeans.labels_  # 0 또는 1로 표시됨
    df['cluster'] = labels

    # 시각화
    plt.figure(figsize=(8,6))
    plt.scatter(X[:,0], X[:,1], c=labels, cmap='viridis', alpha=0.5)
    plt.xlabel('Damage')
    plt.ylabel('ZLOA')
    plt.title('K-Means Clustering (2 Clusters)')
    plt.show()




def DB_scan():

    X = df[['user_damage', 'user_zloa_score']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # DBSCAN 모델 설정
    # eps와 min_samples는 데이터 스케일, 분포에 따라 튜닝이 필요
    dbscan = DBSCAN(eps=0.2, min_samples=5)  # 예시값: eps=3, min_samples=5
    labels = dbscan.fit_predict(X_scaled)

    # -1은 노이즈(이상치)로 간주
    df['cluster'] = labels

    # 클러스터별로 구분
    inliers = df[df['cluster'] != -1]  # 정상 클러스터
    outliers = df[df['cluster'] == -1] # 노이즈(이상치)

    # 시각화
    plt.figure(figsize=(8, 6))

    # 정상 클러스터(각 cluster마다 다른 색)
    unique_clusters = sorted(inliers['cluster'].unique())
    for c in unique_clusters:
        cluster_data = inliers[inliers['cluster'] == c]
        plt.scatter(cluster_data['user_damage'], cluster_data['user_zloa_score'], label=f'Cluster {c}', alpha=0.7)

    # 노이즈(이상치)
    if not outliers.empty:
        plt.scatter(outliers['user_damage'], outliers['user_zloa_score'],
                    color='red', marker='x', label='Outliers')

    plt.title("DBSCAN Clustering")
    plt.xlabel("Damage")
    plt.ylabel("ZLOA")
    plt.legend()
    plt.show()

# %%

DB_scan()