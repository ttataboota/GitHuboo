#%%

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt


def chi():
    data = np.array([[36, 42],  # ALS 기반
                        [29, 39]])  # Pearson 유사도 기반

    row_sum= data.sum(axis=1, keepdims=True)  # 각 알고리즘의 총 평가 수
    col_sum = data.sum(axis=0, keepdims=True)  # Good과 Bad의 총 평가 수
    total = data.sum()  # 전체 평가 수

    # 기대값(기대 빈도) 계산 (Expected Counts)
    expected = (row_sum @ col_sum) / total

    # 카이제곱 계산
    chi2_statistic = ((data - expected) ** 2 / expected).sum()

    # p-value
    p_value = stats.chi2.sf(chi2_statistic, 1)  #자유도 1

    # 결과 출력
    print (f"카이제곱 통계량 : {chi2_statistic} , p_value : {p_value}")

def beta():
    # 사전확률 50:50 으로 설정
    alpha_als, beta_als = 1, 1
    alpha_pearson, beta_pearson = 1, 1


    #data      
    good_als, bad_als = 36, 42
    good_pearson, bad_pearson = 29, 39

    # 데이터 업데이트 (사후 확률)
    alpha_als += good_als
    beta_als += bad_als

    alpha_pearson += good_pearson
    beta_pearson += bad_pearson

    # 베타 분포 생성
    x = np.linspace(0, 1, 1000)
    pdf_als = stats.beta.pdf(x, alpha_als, beta_als)
    pdf_pearson = stats.beta.pdf(x, alpha_pearson, beta_pearson)

    plt.figure(figsize=(10, 5))
    plt.plot(x, pdf_als, label="ALS", linestyle='-', linewidth=2, color='blue')
    plt.plot(x, pdf_pearson, label="Pearson", linestyle='--', linewidth=2, color='red')
    plt.fill_between(x, pdf_als, alpha=0.2, color='blue')
    plt.fill_between(x, pdf_pearson, alpha=0.2, color='red')
    plt.legend()
    plt.xlabel("Good Rate")
    plt.ylabel("Density")
    plt.show()

    # 베타 분포에서 샘플을 생성하여 비교
    n_samples = 100000 
    samples_als = np.random.beta(alpha_als, beta_als, n_samples)
    samples_pearson = np.random.beta(alpha_pearson, beta_pearson, n_samples)

    # ALS 기반 알고리즘이 Pearson 기반보다 높은 확률을 가질 확률 계산
    prob_als_better = np.mean(samples_als > samples_pearson)
    print(f"ALS 기반 알고리즘이 Pearson 기반보다 높은 확률 : {prob_als_better}")


beta()
