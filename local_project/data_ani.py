from sklearn.neighbors import NearestNeighbors
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.sparse import csr_matrix

df = pd.read_csv("df_champ_usage.csv")
data_sparse = csr_matrix(df.values)


# k-최근접 이웃 계산 (k = min_samples)
min_samples = 5
neighbors = NearestNeighbors(n_neighbors=min_samples,metric='cosine')
neighbors_fit = neighbors.fit(data_sparse)
distances, indices = neighbors_fit.kneighbors(data_sparse)

# 각 포인트의 k번째 이웃 거리 계산 (오름차순 정렬)
distances = np.sort(distances[:, min_samples - 1])  # min_samples번째 이웃 거리

# K-거리 플롯
plt.plot(distances)
plt.title("K-Nearest Neighbor Distance Plot")
plt.xlabel("Data Points (sorted)")
plt.ylabel("k-Nearest Neighbor Distance")
plt.grid()
plt.show()
