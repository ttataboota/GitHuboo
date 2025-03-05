#%%
import numpy as np


def prob_setting_B(n):
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
    
    T = np.zeros((n+1, n+1))

    for lvl in range(1,n):
        i = lvl
        p_s, p_f, p_r = prob_table[lvl]

        T[i, i-1] = p_f #실패
        T[i, 0] = p_r # 도망
        
        if lvl<n-1: # 1 to n-2 단계
            T[i, i+2] = p_s * 0.05 # 대성공 
            T[i, i+1] = p_s * 0.95 # 성공
        else: # n-1 단계
            T[i, i+1] = p_s # 성공


    # 0, n 단계 는 흡수상태
    T[0,0] = 1 
    T[n,n] = 1

    # 2단계에선 실패해도 단계 유지임
    T[2,2]=0.4

    return T


T=prob_setting_B(8)


#%%

def octo_prob(now, goal, now_count):
    if now>=goal:
        print("현재 단계보다 높은 목표를 설정하세요")
        return 0
    elif goal>9:
        print("9단계 이하의 목표를 설정하세요")
        return 0
    elif now_count>=100:
        print("문어가 밥을 다 먹었습니다. 내일하세요.")
        return 0 
    p= np.zeros(goal+1)
    p[now] = 1
    T=prob_setting_B(goal)
    T_n = np.linalg.matrix_power(T, 100-now_count) 

    octo= p @ T_n

    for lvl, prob in enumerate(octo):
        print(f"{lvl}단계 : {(prob*100):.4f}%")




octo_prob(4,5,98)
