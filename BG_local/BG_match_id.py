import requests
from bs4 import BeautifulSoup
import pandas as pd
import time



# ✅ 요청을 보낼 URL
url = "https://pubg.op.gg/leaderboard"

# ✅ 필요한 헤더 (User-Agent 포함)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Referer": "https://pubg.op.gg/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
}

response = requests.get(url, headers=headers)

# ✅ 응답 확인
if response.status_code == 200:
    print("✅ 데이터 요청 성공!")
    
    # ✅ BeautifulSoup로 HTML 파싱
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 두 개의 클래스 중 하나라도 포함하는 <a> 태그 찾기 (CSS Selector 사용)
    user_elements = soup.select("a.leader-board-top3__nickname, a.leader-board__nickname")
    
    # ✅ 유저 이름 리스트 추출
    user_names = [user.text.strip() for user in user_elements]



#내 api key
api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJhMTA2NjVlMC0wMDI5LTAxM2ItMjE3MS0yNzQ4YzRhN2Q1ZDYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjYwNzIwMjQyLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii01NGI0MDRmMy1kZDFhLTQwMzItYWJlMC1mMGU5ZWE3NDQxNzUifQ.wNUumN93avLiYsfnAv3JAJycd4V2jcxWdFOzgqNmVcc'

platform='steam'

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/vnd.api+json"
}



def get_match_list(user_names):
  
  global platform, headers

  match_id_list=[]

  for i in user_names:
    player_name = i

    url = f"https://api.pubg.com/shards/{platform}/players?filter[playerNames]={player_name}"

    # 🔹 API 요청
    response = requests.get(url, headers=headers)

    # 🔹 응답 확인
    if response.status_code == 200:
        data = response.json()
        match_ids = [match["id"] for match in data["data"][0]["relationships"]["matches"]["data"]]  # 최근 매치 ID 리스트
        match_id_list.extend(match_ids)
    else:
      print("에러 발생")
    
    time.sleep(10)

  match_id_list=list(set(match_id_list))
  match_id_list = pd.DataFrame(match_id_list, columns=["match_id"])
  match_id_list.to_csv(f"match_id_list.csv", index=False)
  
  return match_id_list

match_ids=get_match_list(user_names)
