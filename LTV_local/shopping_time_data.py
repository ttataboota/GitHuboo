#%%


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# raw_data=pd.read_csv("data/data.csv",encoding="UTF-8")


# # datetime 형식으로 변환 + 일 단위 데이터까지면 충분
# raw_data['발주일'] = pd.to_datetime(raw_data['발주일'])
# data=raw_data[['주문번호', '품목별 주문번호', '총 결제금액', '수령인', '발주일']]


# # 시간(hour) 추출
# data['발주일_hour'] = data['발주일'].dt.hour

# # 시간대별 결제 건수 집계
# hourly_counts = data.groupby('발주일_hour').size().reset_index(name='count')


# # 시각화: 바 차트
# plt.figure(figsize=(8, 4))
# plt.bar(hourly_counts['발주일_hour'], hourly_counts['count'], color='skyblue')
# plt.xlabel('Hour of Day')
# plt.ylabel('Number of Payments')
# plt.title('Number of Payments by Hour')
# plt.xticks(range(0, 24))
# plt.show()



# # 시간별 결제 건수, 결제 금액 총합 및 평균 계산
# agg_data = data.groupby('발주일_hour')['총 결제금액'].agg(['sum', 'mean','median', 'count']).reset_index()

# # Dual-Axis 차트 생성
# fig, ax1 = plt.subplots(figsize=(10, 6))

# # 왼쪽 축: 결제 건수 (바 차트)
# ax1.bar(agg_data['발주일_hour'], agg_data['count'], color='skyblue', label='Payment Count')
# ax1.set_xlabel('Hour of Day')
# ax1.set_ylabel('Payment Count', color='blue')

# # 오른쪽 축: 평균 결제 금액 (선 그래프)
# ax2 = ax1.twinx()
# ax2.plot(agg_data['발주일_hour'], agg_data['median'], color='red', marker='o', label='median Payment Amount')
# ax2.set_ylabel('Average Payment Amount', color='red')


# plt.title('median Payment Amount')
# plt.xticks(range(0, 24))
# plt.show()


# # Dual-Axis 차트 생성
# fig, ax1 = plt.subplots(figsize=(10, 6))

# # 왼쪽 축: 결제 건수 (바 차트)
# ax1.bar(agg_data['발주일_hour'], agg_data['count'], color='skyblue', label='Payment Count')
# ax1.set_xlabel('Hour of Day')
# ax1.set_ylabel('Payment Count', color='blue')

# # 오른쪽 축: 평균 결제 금액 (선 그래프)
# ax2 = ax1.twinx()
# ax2.plot(agg_data['발주일_hour'], agg_data['mean'], color='red', marker='o', label='mean Payment Amount')
# ax2.set_ylabel('Average Payment Amount', color='red')


# plt.title('Average Payment Amount')
# plt.xticks(range(0, 24))
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt

raw_data=pd.read_csv("data/data.csv",encoding="UTF-8")


raw_data['발주일'] = pd.to_datetime(raw_data['발주일'])
df=raw_data[['주문번호', '품목별 주문번호', '총 결제금액', '수령인', '발주일']]

#%%

# 시간과 요일 추출
df['hour'] = df['발주일'].dt.hour
df['weekday'] = df['발주일'].dt.day_name()  # 요일 이름 추출

# 요일 순서를 정렬(선택사항)
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)




# 요일 및 시간별 결제 금액 중앙값 집계 (또는 합계, count 등 원하는 값)
agg_data = df.groupby(['weekday', 'hour'])['발주일'].median().reset_index()

# 피벗 테이블 생성: 행은 요일, 열은 시간, 값은 결제 금액 중앙값
pivot_data = df.pivot_table(values='발주일', index='weekday', columns='hour', aggfunc='median')

# 히트맵 시각화
plt.figure(figsize=(10, 6))
sns.heatmap(pivot_data, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title('요일 및 시간대별 결제 금액 중앙값')
plt.xlabel('Hour of Day')
plt.ylabel('Weekday')
plt.show()

# %%
