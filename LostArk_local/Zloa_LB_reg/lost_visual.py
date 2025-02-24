#%%

import pandas as pd
import matplotlib.pyplot as plt

user_data_damage=pd.read_csv('user_data_damage2.csv')
user_data_zloa=pd.read_csv('user_data_zloa.csv')

merged_df = user_data_damage.merge(user_data_zloa, on='0', suffixes=('_damage', '_zloa'))


# X축: user_data_damage['1'], Y축: user_data_zloa['1']
x_values = merged_df['1_damage']
y_values = merged_df['1_zloa']

# Scatter plot 그리기
plt.figure(figsize=(8, 6))
plt.scatter(x_values, y_values, alpha=0.7, edgecolors='k')

# 그래프 스타일
plt.xlabel('Damage Data')
plt.ylabel('ZLOA Data')
plt.title('Scatter Plot of Damage vs. ZLOA')

plt.show()