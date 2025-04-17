#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from lifetimes import GammaGammaFitter
from lifetimes import ParetoNBDFitter
from lifetimes import BetaGeoFitter

from feature_engine.outliers import OutlierTrimmer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from kneed import KneeLocator
import seaborn as sns



raw_data=pd.read_csv("data/data.csv",encoding="UTF-8")


# datetime 형식으로 변환 + 일 단위 데이터까지면 충분
raw_data['발주일'] = pd.to_datetime(raw_data['발주일'])
raw_data['발주일'] = raw_data['발주일'].dt.date

data=raw_data[['주문번호', '품목별 주문번호', '총 결제금액', '수령인', '발주일']]





data=data.groupby(['수령인','발주일']).agg(
    cost=('총 결제금액','sum')
)

data.reset_index(inplace=True)  # MultiIndex 해제




gg_summary = data.groupby('수령인').agg(
    freq=('cost', 'count'),       # 구매 횟수
    mean_cost=('cost', 'mean')   # 평균 결제금액
).reset_index()

# Gamma-Gamma 모델은 구매 횟수가 최소 2 이상인 고객만 사용 가능
gg_summary = gg_summary[gg_summary['freq'] > 1]

# 모델 적합
ggf = GammaGammaFitter(penalizer_coef=0.01)  # penalizer << 과적합 방지 하이퍼파라미터
ggf.fit(gg_summary['freq'], gg_summary['mean_cost'])

#각 고객의 예상 평균 거래 금액 예측
gg_summary['predicted_cost'] = ggf.conditional_expected_average_profit(
    gg_summary['freq'],
    gg_summary['mean_cost']
).round(2)

gg_summary['mean_cost'] = gg_summary['mean_cost'].round(2)





pareto_summary = data.groupby('수령인').agg(
    re_freq=('cost', lambda x: x.count() - 1),  # 첫 구매 제외(-1) 재구매 횟수
    recency=('발주일', lambda x: (x.max() - x.min()).days),  # 최초구매~최근구매 간격
    T=('발주일', lambda x: (data['발주일'].max() - x.min()).days)  # 최초구매~현재까지 기간
).reset_index()

#두가지 방법론으로 진행해보자! 감마-지수(pareto_summary) // 베타-기하(bgnbd_summary)

bgnbd_summary=pareto_summary.copy()

pareto_summary = pareto_summary[pareto_summary['re_freq'] >= 0]

# Pareto/NBD 모델 피팅
pareto_model = ParetoNBDFitter(penalizer_coef=0.01)
pareto_model.fit(pareto_summary['re_freq'], pareto_summary['recency'], pareto_summary['T'])

# 90일 동안 고객의 기대 거래 횟수 예측
pareto_summary['expected_purchases_90d'] = pareto_model.conditional_expected_number_of_purchases_up_to_time(
    90,
    pareto_summary['re_freq'],
    pareto_summary['recency'],
    pareto_summary['T']
).round(2)


merged_df = pareto_summary.merge(gg_summary, on='수령인')

# 예상 구매량 * 예측 지출액 계산
merged_df['expected_total_revenue'] = (merged_df['expected_purchases_90d'] * merged_df['predicted_cost']).round(2)


merged_df.sort_values(by='expected_total_revenue',ascending=False,inplace=True)




# 'target' 열의 이상치를 IQR 방식으로 제거합니다.
otr = OutlierTrimmer(capping_method='iqr', tail='both', fold=1.5, variables=['mean_cost'])
df = otr.fit_transform(merged_df)




x_values = df['re_freq']
y_values = df['mean_cost']
plt.figure(figsize=(8, 6))
plt.scatter(x_values, y_values, alpha=0.7, edgecolors='k')
plt.show()



#상관 계수 분석  << 사실상 새로운 인사이트 없음.
df=merged_df.drop(columns=['수령인','expected_purchases_90d','freq','predicted_cost','expected_total_revenue']).copy()

pearson_corr = df.corr(method='pearson')
print("Pearson 상관계수:\n", pearson_corr)

spearman_corr = df.corr(method='spearman')
print("\nSpearman 상관계수:\n", spearman_corr)





def kmean_4():
    X = df[['re_freq','mean_cost']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)


    kmeans = KMeans(n_clusters=4, random_state=42,init='k-means++')
    kmeans.fit(X_scaled)

    labels = kmeans.labels_ 
    df['cluster'] = labels

    plt.figure(figsize=(8,6))
    plt.scatter(X[:,0], X[:,1],c=labels, cmap='viridis', alpha=0.5)
    plt.show()

def scree_plot_KneeLocator():
    X = df[['re_freq','mean_cost']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # NearestNeighbors로 거리 계산 (정규화된 데이터 사용)
    min_samples = 4
    neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors_fit = neighbors.fit(X_scaled)
    distances, _ = neighbors_fit.kneighbors(X_scaled)


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



def DB_scan(x):

    X = df[['re_freq','mean_cost']].values

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
        plt.scatter(cluster_data['re_freq'], cluster_data['mean_cost'], label=f'Cluster {c}', alpha=0.7)

    # 이상치
    if not outliers.empty:
        plt.scatter(outliers['re_freq'], outliers['mean_cost'],
                    color='red', marker='x', label='Outliers')


    plt.legend()
    plt.show()


    return df

def re_plot(x):
    temp=df[df['re_freq']==x]
    X = temp[['re_freq','mean_cost']].values

    plt.figure(figsize=(8,6))
    plt.scatter(X[:,0], X[:,1])
    plt.show()



def re_plot(x):
    temp = df[df['re_freq'] == x]
    plt.figure(figsize=(8,6))
    sns.histplot(temp['mean_cost'], bins=30, kde=True)
    plt.title(f"Mean Cost Distribution for re_freq = {x}")
    plt.xlabel("Mean Cost")
    plt.ylabel("Frequency")
    plt.show()

def re_boxplot(x):
    temp = df[df['re_freq'] == x]
    plt.figure(figsize=(8,6))
    sns.boxplot(x=temp['mean_cost'])
    plt.title(f"Mean Cost Boxplot for re_freq = {x}")
    plt.xlabel("Mean Cost")
    plt.show()



#%%











bgf = BetaGeoFitter(penalizer_coef=0.01)  # 과적합 방지용 패널티
bgf.fit(
    frequency=bgnbd_summary['re_freq'],
    recency=bgnbd_summary['recency'],
    T=bgnbd_summary['T']
)


prediction_days = 90  # 예시로 90일 설정
bgnbd_summary['expected_purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(
    prediction_days,
    bgnbd_summary['re_freq'],
    bgnbd_summary['recency'],
    bgnbd_summary['T']
).round(2)



merged_df_2 = bgnbd_summary.merge(gg_summary, on='수령인')

# 예상 구매량 * 예측 지출액 계산
merged_df_2['expected_total_revenue'] = (merged_df_2['expected_purchases'] * merged_df_2['predicted_cost']).round(2)


merged_df_2.sort_values(by='expected_total_revenue',ascending=False,inplace=True)


#%%
