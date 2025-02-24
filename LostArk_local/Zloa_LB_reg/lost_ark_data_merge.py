#%%

import requests
import json
from itertools import chain
import pandas as pd
import matplotlib.pyplot as plt

user_data_zloa=[]


for i in range(8):
    df=pd.read_csv(f"user_data_zloa_df{i+1}.csv",encoding="utf-8-sig")
    user_data_zloa.append(df)

user_data_zloa_df = pd.concat(user_data_zloa, ignore_index=True)

user_data_zloa_df = user_data_zloa_df[~((user_data_zloa_df == 0) | (user_data_zloa_df.isnull())).any(axis=1)]

user_data_zloa_df = user_data_zloa_df.drop_duplicates(subset='user_name', keep='first').reset_index(drop=True)




user_data_damage=pd.read_csv("user_data_damage2.csv",encoding="utf-8-sig")

merged_df=pd.merge(user_data_zloa_df,user_data_damage,on='user_name',how='inner')

merged_df.to_csv("user_data_merged.csv", index=False, encoding="utf-8-sig")


# #%%
# x_values = merged_df['user_damage']
# y_values = merged_df['user_zloa_score']

# # Scatter plot 그리기
# plt.figure(figsize=(8, 6))
# plt.scatter(x_values, y_values, alpha=0.7, edgecolors='k')

# # 그래프 스타일
# plt.xlabel('Damage Data')
# plt.ylabel('ZLOA Data')
# plt.title('Scatter Plot of Damage vs. ZLOA')

# plt.show()
# # %%
