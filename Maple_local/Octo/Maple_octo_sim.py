#%%

import numpy as np


# A버전은 대성공률 고정
def prob_setting_A():
    # 1~8단계 확률
    prob_table = {
        1: (1.00, 0.00, 0.00),
        2: (0.60, 0.00, 0.00),  # 2단계는 실패해도 단계 유지
        3: (0.50, 0.50, 0.00),
        4: (0.40, 0.60, 0.00),
        5: (0.307, 0.693, 0.00),
        6: (0.205, 0.765, 0.03),
        7: (0.103, 0.857, 0.04),
        8: (0.05,  0.90,  0.05),

        "hit" : 0.005  # 대성공 확률 고정
    }

    T = np.zeros((10, 10))

    for lvl in range(1,9):
        i = lvl
        p_s, p_f, p_r = prob_table[lvl]

        T[i, i-1] = p_f #실패
        T[i, 0] = p_r # 도망
        
        if lvl<8: # 1-7 단계
            T[i, i+2] = prob_table['hit'] # 대성공 
            T[i, i+1] = p_s - prob_table['hit'] # 성공
        else: # 8단계
            T[i, i+1] = p_s # 성공


    # 0, 9 단계 는 흡수상태
    T[0,0] = 1 
    T[9,9] = 1

    # 2단계에선 실패해도 단계 유지임
    T[2,2]=0.4

    return T


# B버전은 대성공률 단계마다 다름
def prob_setting_B():
    # 1~8단계 확률
    prob_table = {
        1: (1.00, 0.00, 0.00),
        2: (0.60, 0.00, 0.00),  # 2단계는 실패해도 단계 유지
        3: (0.50, 0.50, 0.00),
        4: (0.40, 0.60, 0.00),
        5: (0.307, 0.693, 0.00),
        6: (0.205, 0.765, 0.03),
        7: (0.103, 0.857, 0.04),
        8: (0.05,  0.90,  0.05),

    }

    #대성공은 각 단계의 성공확률의 5퍼센트로 가정.
    
    T = np.zeros((10, 10))

    for lvl in range(1,9):
        i = lvl
        p_s, p_f, p_r = prob_table[lvl]

        T[i, i-1] = p_f #실패
        T[i, 0] = p_r # 도망
        
        if lvl<8: # 1-7 단계
            T[i, i+2] = p_s * 0.05 # 대성공 
            T[i, i+1] = p_s * 0.95 # 성공
        else: # 8단계
            T[i, i+1] = p_s # 성공


    # 0, 9 단계 는 흡수상태
    T[0,0] = 1 
    T[9,9] = 1

    # 2단계에선 실패해도 단계 유지임
    T[2,2]=0.4

    return T


T=prob_setting_B()

# 초기 분포 (1단계에서 시작)
p0 = np.zeros(10)
p0[1] = 1.0 


def n_oct_feeding(T, p0, n):
    p = p0.copy()
    T_n = np.linalg.matrix_power(T, n) # 마콥체인 전이 행렬 거듭제곱으로 n회후 위치 확률 행렬 구하기
    return p @ T_n  


step=100

octo = n_oct_feeding(T, p0, step)


sum=0
for lvl, prob in enumerate(octo):
    print(f"{lvl}단계 : {(prob*100):.4f}%")
    sum+=prob
print(f"각 단계별 확률 총합계 : {sum}" )
# %%


