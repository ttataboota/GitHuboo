#%%
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from itertools import chain
from playwright.sync_api import sync_playwright
import time
import pandas as pd


# 세션 객체 사용
with requests.Session() as session:
    user_names = list(chain.from_iterable(
        [name['name'] for name in json.loads(session.get(
            f'https://secapi.korlark.com/lostark/ranking/character?page={i+1}&limit=3&job=11&engrave=분노의+망치'
        ).text)] for i in range(10,20)
    ))



def convert_number(text: str) -> int:
    # 공백 제거(혹은 공백 허용 정규식 사용)
    text = text.replace(" ", "")  
    
    # 정규식 패턴: (억), (만), (나머지 숫자)
    pattern = r'(?:(\d+)억)?(?:(\d+)만)?(\d+)?'
    match = re.match(pattern, text)

    if not match:
        # 매칭 안 되면 0이나 에러 처리
        return 0

    # None 방지
    eok = match.group(1) or "0"  # 억
    man = match.group(2) or "0"  # 만
    rest = match.group(3) or "0" # 나머지 숫자

    # 정수 변환 후 계산
    eok_val = int(eok) * 100000000
    man_val = int(man) * 10000
    rest_val = int(rest)

    total = eok_val + man_val + rest_val
    
    return round(total/ 10**8, 2)





# 크롬 옵션 설정 (필요 시 추가 옵션 사용 가능)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') 

# ChromeDriverManager를 사용해 크롬 드라이버를 자동 설치/업데이트
service = Service(ChromeDriverManager().install())

# 위에서 설정한 service와 옵션을 사용하여 드라이버 생성
driver = webdriver.Chrome(service=service, options=chrome_options)



user_data_damage=[]

for name in user_names:
    # LostBuilds 웹사이트 열기
    url = f'https://lostbuilds.com/info/{name}'
    driver.get(url)
    time.sleep(2)

    try:
        element = driver.find_element(By.XPATH, '//*[contains(text(), "억")]')
        damage=convert_number(element.text)
        user_data_damage.append((name,damage))
        print(f"유저명: {name} , 데미지: {damage}억 추출 완료")
    except:
        continue

driver.quit()

user_data_damage_df=pd.DataFrame(user_data_damage,columns=['user_name','user_damage'])

user_data_damage_df.to_csv('user_data_damage3.csv',index=False,encoding="utf-8-sig")

