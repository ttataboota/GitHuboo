#%%

import requests
import json
from itertools import chain
import pandas as pd
import matplotlib.pyplot as plt

user_data_zloa=[]
for i in range(12):
    df=pd.read_csv(f"user_data_zloa_df{i+1}.csv",encoding="utf-8-sig")
    user_data_zloa.append(df)

user_data_zloa_df = pd.concat(user_data_zloa, ignore_index=True)
user_data_zloa_df = user_data_zloa_df[~((user_data_zloa_df == 0) | (user_data_zloa_df.isnull())).any(axis=1)]
user_data_zloa_df = user_data_zloa_df.drop_duplicates(subset='user_name', keep='first').reset_index(drop=True)


user_data_damage_2=pd.read_csv("user_data_damage2.csv",encoding="utf-8-sig")
user_data_damage_3=pd.read_csv("user_data_damage3.csv",encoding="utf-8-sig")
user_data_damage=pd.concat([user_data_damage_2,user_data_damage_3],ignore_index=True)
user_data_damage = user_data_damage.drop_duplicates(subset='user_name', keep='first').reset_index(drop=True)

merged_df=pd.merge(user_data_zloa_df,user_data_damage,on='user_name',how='inner')

merged_df.to_csv("user_data_merged_2.csv", index=False, encoding="utf-8-sig")

