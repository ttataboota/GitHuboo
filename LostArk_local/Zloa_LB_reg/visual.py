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
from sklearn.neighbors import NearestNeighbors
from kneed import KneeLocator
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


df=pd.read_csv("user_data_merged_2.csv",encoding="utf-8-sig")

def iso_forest():

    X = df[['user_damage', 'user_zloa_score']].values



    iso_forest = IsolationForest(contamination=0.2, random_state=42)
    iso_forest.fit(X)
    labels = iso_forest.predict(X)

    # -1: 이상치
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



def draw_scattering():
    x_values = df['user_damage']
    y_values = df['user_zloa_score']
    plt.figure(figsize=(8, 6))
    plt.scatter(x_values, y_values, alpha=0.7, edgecolors='k')
    plt.xlabel('Damage Data')
    plt.ylabel('ZLOA Data')

    plt.show()





def kmean_2():
    X = df[['user_damage', 'user_zloa_score']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)


    kmeans = KMeans(n_clusters=2, random_state=42,init='k-means++')
    kmeans.fit(X_scaled)

    labels = kmeans.labels_ 
    df['cluster'] = labels

    plt.figure(figsize=(8,6))
    plt.scatter(X[:,0], X[:,1], c=labels, cmap='viridis', alpha=0.5)
    plt.xlabel('Damage')
    plt.ylabel('ZLOA')
    plt.title('K-Means Clustering (2 Clusters)')
    plt.show()




def DB_scan(x):

    X = df[['user_damage', 'user_zloa_score']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)



    dbscan = DBSCAN(eps=x, min_samples=4)  
    labels = dbscan.fit_predict(X_scaled)



    # -1은 노이즈(이상치)로 간주
    df['cluster'] = labels

    inliers = df[df['cluster'] != -1]  # 정상 클러스터
    outliers = df[df['cluster'] == -1] # 노이즈(이상치)


    plt.figure(figsize=(8, 6))

    # 정상 클러스터(각 cluster마다 다른 색)
    unique_clusters = sorted(inliers['cluster'].unique())
    for c in unique_clusters:
        cluster_data = inliers[inliers['cluster'] == c]
        plt.scatter(cluster_data['user_damage'], cluster_data['user_zloa_score'], label=f'Cluster {c}', alpha=0.7)

    # 이상치
    if not outliers.empty:
        plt.scatter(outliers['user_damage'], outliers['user_zloa_score'],
                    color='red', marker='x', label='Outliers')

    plt.title("DBSCAN Clustering")
    plt.xlabel("Damage")
    plt.ylabel("ZLOA")
    plt.legend()
    plt.show()


    return df


def scree_plot_KneeLocator():
    X = df[['user_damage', 'user_zloa_score']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # NearestNeighbors로 거리 계산 (정규화된 데이터 사용)
    min_samples = 5
    neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors_fit = neighbors.fit(X_scaled)
    distances, indices = neighbors_fit.kneighbors(X_scaled)


    distances = np.sort(distances[:, min_samples - 1])

    plt.figure(figsize=(8, 5))
    plt.plot(distances, color='blue')
    plt.xlabel('Data Points sorted by distance', fontsize=12)
    plt.ylabel(f'{min_samples}-th Nearest Neighbor Distance (Standardized)', fontsize=12)
    plt.title('K-Distance Graph (Standardized Data) for DBSCAN', fontsize=14)
    plt.grid(True)
    plt.show()


    # 5. KneeLocator로 Knee Point 찾기
    kneedle = KneeLocator(range(len(distances)), distances, curve="convex", direction="increasing")
    knee_point = kneedle.knee
    eps_value = distances[knee_point]

    # 6. 결과 시각화
    plt.figure(figsize=(8, 5))
    plt.plot(distances, label='K-Distance Graph')
    plt.axvline(knee_point, color='r', linestyle='--', label=f'Knee at index {knee_point}')
    plt.axhline(eps_value, color='g', linestyle='--', label=f'Estimated eps ≈ {eps_value:.3f}')
    plt.xlabel('Data Points sorted by distance', fontsize=12)
    plt.ylabel(f'{min_samples}-th Nearest Neighbor Distance (Standardized)', fontsize=12)
    plt.title('Knee Point Detection using KneeLocator', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.show()

    print(f"Recommended eps value: {eps_value:.3f}")


# 위 방법들을 통하면 0.33 이 가장 적합 하나, 카던 관련 세팅을 분류하기 위해선 eps 값이 더 낮아야한다.

df=DB_scan(0.22)


# 선형회귀 결과 확인


selected_clusters = [0, 1, 2]
filtered_df = df[df['cluster'].isin(selected_clusters)]

# 여기 바꿔서 확인해야 할 수도..?
X = filtered_df[['user_damage']].values  # 독립 변수
y = filtered_df['user_zloa_score'].values  # 종속 변수


reg = LinearRegression()
reg.fit(X, y)


X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
y_pred = reg.predict(X_pred)


plt.figure(figsize=(8, 5))
plt.scatter(X, y, c=filtered_df['cluster'], cmap='viridis', label='Data Points', alpha=0.6)
plt.plot(X_pred, y_pred, color='red', linewidth=2, label='Regression Line')
plt.xlabel('Damage')
plt.ylabel('ZLOA')
plt.title('Linear Regression on Clusters 0, 1, 2')
plt.legend()
plt.grid(True)
plt.show()

print(f"회귀식: ZLOA = {reg.coef_[0]:.3f} * Damage + {reg.intercept_:.3f}")
print(f"R^2 Score: {reg.score(X, y):.3f}")



#2차 회귀 진행

poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)  # X에 x^2 항 추가

reg = LinearRegression()
reg.fit(X_poly, y)

X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
X_pred_poly = poly.transform(X_pred)
y_pred = reg.predict(X_pred_poly)

plt.figure(figsize=(8, 5))
plt.scatter(X, y, c=filtered_df['cluster'], cmap='viridis', label='Data Points', alpha=0.6)
plt.plot(X_pred, y_pred, color='red', linewidth=2, label='2nd Degree Regression')
plt.xlabel('Damage')
plt.ylabel('ZLOA')
plt.title('2nd Degree Polynomial Regression on Clusters 0, 1, 2')
plt.legend()
plt.grid(True)
plt.show()

coeffs = reg.coef_
intercept = reg.intercept_
print(f"회귀식: ZLOA = {coeffs[2]:.4f} * Damage^2 + {coeffs[1]:.4f} * Damage + {intercept:.4f}")
print(f"R^2 Score: {reg.score(X_poly, y):.4f}")


# %%
