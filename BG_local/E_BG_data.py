#%%

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns


data=[]

for i in range(1,6):
    df=pd.read_csv(f"data/data_all_random{i}.csv",encoding="UTF-8",)
    data.append(df)

data_final=pd.concat(data,ignore_index=True)

data_final.to_csv("data/data_final.csv", encoding="UTF-8", index=False)

data_final[(data_final['fire_count'] > 20) & (data_final['weapon']=='AUG')]\
    .groupby(['weapon'])\
    .agg(hit_mean=('hit', 'mean'), 
         hit_count=('hit', 'count'),
         fire_count_mean=('fire_count', 'mean'))

AUG=data_final[(data_final['fire_count'] > 20) & (data_final['weapon']=='AUG')]


sns.boxplot(AUG)

# %%
