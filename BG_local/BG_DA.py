#%%

import pandas as pd
import matplotlib.pyplot as plt

data1=pd.read_csv('data_all_random.csv')
data2=pd.read_csv('data_all_random2.csv')
data3=pd.read_csv('data_all_random3.csv')
data4=pd.read_csv('data_all.csv')
data5=pd.read_csv('data_all2.csv')

data=[data1,data2,data3,data4,data5]

BG_data=pd.concat(data, ignore_index=True)

#%%

plt.figure(figsize=(18, 6))

# 🔹 Boxplot 생성
BG_data.boxplot(column='hit', by='weapon', grid=False, vert=True, patch_artist=True)

# 그래프 설정
plt.title("Hit Distribution by Weapon", fontsize=14)
plt.suptitle("")  # 기본 제목 제거
plt.xlabel("Weapon", fontsize=12)
plt.ylabel("Hit Value", fontsize=12)

# X축 레이블 회전 및 크기 조정
plt.xticks(rotation=45, ha='right', fontsize=10)

# 그래프 출력
plt.show()
# %%
