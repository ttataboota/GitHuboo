#%%

# 목표 : 미끼상품(넥타이) 는 과연 미끼가 되고 있는가?

import pandas as pd


raw_data=pd.read_csv("data/data.csv",encoding="UTF-8")


# datetime 형식으로 변환 + 일 단위 데이터까지면 충분
raw_data['발주일'] = pd.to_datetime(raw_data['발주일'])
raw_data['발주일'] = raw_data['발주일'].dt.date


#넥타이 구매 고객 필터링
filtered_data = raw_data[raw_data['주문상품명'].str.contains('넥타이', na=False)]
data=filtered_data[['주문번호', '품목별 주문번호', '총 결제금액', '수령인', '발주일']]

data=data.groupby(['수령인','발주일']).agg(
    cost=('총 결제금액','sum')
)

data.reset_index(inplace=True)  # MultiIndex 해제

summary = data.groupby('수령인').agg(
    re_freq=('cost', lambda x: x.count() - 1),  # 첫 구매 제외(-1) 재구매 횟수
    recency=('발주일', lambda x: (x.max() - x.min()).days),  # 최초구매~최근구매 간격
    T=('발주일', lambda x: (data['발주일'].max() - x.min()).days)  # 최초구매~현재까지 기간


).reset_index()

#넥타이 재구매율은 약 10퍼센트. 미끼만 자꾸 사러오는 사람은 많이 없음!
summary[summary['re_freq']>0] 






# 넥타이를 구매한 이력이 있는 고객의 데이터를 전부 확인 << 넥타이 구매 이후 추가적인 구매가 이루어졌나? 확인해보자

loss_leader= list(raw_data[raw_data['주문상품명'].str.contains('넥타이', na=False)]['수령인'].unique())

loss_data = raw_data[raw_data['수령인'].isin(loss_leader)]

dloss_dataata=loss_data[['주문번호', '품목별 주문번호', '총 결제금액', '수령인', '발주일']]

loss_data=loss_data.groupby(['수령인','발주일']).agg(
    cost=('총 결제금액','sum')
)

loss_data.reset_index(inplace=True)  # MultiIndex 해제

loss_summary = loss_data.groupby('수령인').agg(
    re_freq=('cost', lambda x: x.count() - 1),  # 첫 구매 제외(-1) 재구매 횟수
    recency=('발주일', lambda x: (x.max() - x.min()).days),  # 최초구매~최근구매 간격
    T=('발주일', lambda x: (loss_data['발주일'].max() - x.min()).days)  # 최초구매~현재까지 기간


).reset_index()

len(loss_summary[loss_summary['re_freq']>0])
# 재구매(총구매 횟수-1) 1회: 27 명
# 재구매 2회 이상 : 30 명
# 데이터 자체가 구매한 물품이 전부 나오는거 같진 않다...





# %%
