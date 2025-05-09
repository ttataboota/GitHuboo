import numpy as np
star= np.array([
    [0.0025, 0.9975, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 0
    [0, 0.0550, 0.9450, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 1
    [0, 0, 0.1075, 0.8925, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 2
    [0, 0, 0, 0.1075, 0.8925, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 3
    [0, 0, 0, 0, 0.1600, 0.8400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 4
    [0, 0, 0, 0, 0, 0.2125, 0.7875, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 5
    [0, 0, 0, 0, 0, 0, 0.2650, 0.7350, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 6
    [0, 0, 0, 0, 0, 0, 0, 0.3175, 0.6825, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 7
    [0, 0, 0, 0, 0, 0, 0, 0, 0.3700, 0.6300, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 8
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.4225, 0.5775, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.4750, 0.5250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5275, 0.4725, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 11
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5800, 0.4200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 12
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.6325, 0.3675, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 13
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.6850, 0.3150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 14
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0210, 0, 0, 0.6640, 0.3150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 15
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0210, 0, 0, 0, 0.6640, 0.3150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 16
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0680, 0, 0, 0, 0, 0.7745, 0.1575, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 17
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0680, 0, 0, 0, 0, 0, 0.7745, 0.1575, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 18
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0850, 0, 0, 0, 0, 0, 0, 0.7575, 0.1575, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 19
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1050, 0, 0, 0, 0, 0, 0, 0, 0.5800, 0.3150, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 20
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1275, 0, 0, 0, 0, 0, 0, 0, 0, 0.7150, 0.1575, 0, 0, 0, 0, 0, 0, 0, 0],  # Level 21
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1700, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.6725, 0.1575, 0, 0, 0, 0, 0, 0, 0],  # Level 22
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1800, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7150, 0.1050, 0, 0, 0, 0, 0, 0],  # Level 23
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1800, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7150, 0.1050, 0, 0, 0, 0, 0],  # Level 24
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1800, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7150, 0.1050, 0, 0, 0, 0],  # Level 25
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1860, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7405, 0.0735, 0, 0, 0],  # Level 26
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1900, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7575, 0.0525, 0, 0],  # Level 27
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1940, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7745, 0.0315, 0],  # Level 28
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1980, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.7915, 0.0105],  # Level 29
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0]  # Level 30
])


def star_prob(now, goal):
    if now>=goal:
        print("현재 단계보다 높은 목표를 설정하세요")
        return 0
    elif goal>30:
        print("30단계 이하의 목표를 설정하세요")
        return 0
    p= np.zeros(goal+1)
    p[now] = 1
    T=star[:goal+1,:goal+1].copy()
    T[goal,:]=0
    T[goal,goal]=1
    T_n = np.linalg.matrix_power(T, 1000) 

    star_100= p @ T_n

    for lvl, prob in enumerate(star_100):
        print(f"{lvl}단계 : {(prob*100):.4f}%")


star_prob(0,30)
