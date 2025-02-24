from playwright.sync_api import sync_playwright
import time
import pandas as pd
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
from itertools import chain
from playwright.sync_api import sync_playwright

from playwright.sync_api import sync_playwright, TimeoutError



# 세션 객체 사용
with requests.Session() as session:
    user_names = list(chain.from_iterable(
        [name['name'] for name in json.loads(session.get(
            f'https://secapi.korlark.com/lostark/ranking/character?page={i+1}&limit=3&job=11&engrave=분노의+망치'
        ).text)] for i in range(10,20)
    ))

user_data_zloa = []

count=0


user_names=user_names[500:700]

# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_dev"


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]

    for user_name in user_names:
        print(f"\n🚀 '{user_name}' 검색 시작")

        # ✅ 로딩 스피너가 사라질 때까지 대기
        try:
            page.wait_for_selector("div.loading-spinner", state="hidden", timeout=10000)
            print("✅ 로딩 완료")

        except TimeoutError:
            print("⚠️ 로딩이 10초 안에 끝나지 않았습니다. CAPTCHA가 발생했을 수 있습니다.")
            # ✅ CAPTCHA 대기 로직
            while True:
                try:
                    page.wait_for_selector("div.loading-spinner", state="hidden", timeout=60000)
                    print("✅ CAPTCHA 해결됨. 작업 재개.")
                    break
                except TimeoutError:
                    input("🛑 CAPTCHA를 해결한 후 엔터 키를 눌러주세요...")
                    time.sleep(10)
        # ✅ 검색창에 닉네임 입력
        try:
            search_input_selector = 'input[placeholder="캐릭터 이름을 입력하세요"]'
            search_button_selector = 'button:has(svg.lucide-search)'

            # 검색창 초기화 후 닉네임 입력
            page.fill(search_input_selector, "")
            page.fill(search_input_selector, user_name)

            # 검색 버튼 클릭
            page.click(search_button_selector)

            # ✅ 로딩 스피너가 사라질 때까지 대기
            page.wait_for_selector("div.loading-spinner", state="hidden", timeout=60000)

            # ✅ 결과가 표시되는지 확인
            character_selector = "tr:has(th:text('캐릭터 이름')) td"
            page.wait_for_selector(character_selector, timeout=15000)
            character_element = page.query_selector(character_selector)
            

            time.sleep(3)

            if character_element:
                # 추출한 캐릭터 이름
                extracted_name = character_element.inner_text().strip()
                # ✅ 검색한 이름과 비교
                if extracted_name == user_name:
                    print("✅ 캐릭터 이름이 일치합니다. 결과 확인 완료.")
                else:
                    print(f"⚠️ 캐릭터 이름 불일치! (검색: {user_name}, 추출: {extracted_name})")
                    # 필요 시 로직 추가 (재시도, 오류 처리 등)
                    try:
                        print("재검색을 시작")
                        time.sleep(2)
                        search_input_selector = 'input[placeholder="캐릭터 이름을 입력하세요"]'
                        search_button_selector = 'button:has(svg.lucide-search)'

                        # 검색창 초기화 후 닉네임 입력
                        page.fill(search_input_selector, "")
                        page.fill(search_input_selector, user_name)

                        # 검색 버튼 클릭
                        page.click(search_button_selector)

                        # ✅ 로딩 스피너가 사라질 때까지 대기
                        page.wait_for_selector("div.loading-spinner", state="hidden", timeout=60000)

                        # ✅ 결과가 표시되는지 확인
                        character_selector = "tr:has(th:text('캐릭터 이름')) td"
                        page.wait_for_selector(character_selector, timeout=15000)
                        character_element = page.query_selector(character_selector)
                        time.sleep(3)
                    except:
                        time.sleep(2)
            else:
                print("❌ 캐릭터 이름을 찾지 못했습니다.")

            # ✅ 캐릭터 이름 추출
            if character_element:
                character_name = character_element.inner_text()
                print(f"🎮 캐릭터 이름: {character_name}")
            else:
                print("❌ 캐릭터 이름을 찾지 못했습니다.")
                character_name = None

            # ✅ 최고 환산 점수 추출
            highest_score_selector = "tr:has(th:text('최고 환산 점수')) td"
            try:
                page.wait_for_selector(highest_score_selector, timeout=15000)
                highest_score_element = page.query_selector(highest_score_selector)

                if highest_score_element:
                    highest_score = highest_score_element.inner_text()
                    print(f"🏆 최고 환산 점수: {highest_score}")
                else:
                    print("❌ 최고 환산 점수를 찾지 못했습니다.")
                    highest_score = "0"
            except Exception as e:
                print("❌ 최고 환산 점수 추출 중 오류:", e)
                highest_score = "0"

            # ✅ 결과 저장
            user_data_zloa.append((user_name, highest_score))

        except Exception as e:
            print("❌ 검색 과정 중 오류:", e)
            user_data_zloa.append((user_name, "0"))

        # ✅ 유저별 딜레이 (서버 부하 방지)
        time.sleep(2)  # 필요에 따라 조정 가능
        count+=1
        if count%100==0:
            user_data_zloa_df = pd.DataFrame(user_data_zloa, columns=['user_name', 'user_zloa_score'])
            user_data_zloa_df.to_csv(f"user_data_zloa_df_part_{count/len(user_names)*4}.csv", index=False, encoding="utf-8-sig")
            print(f"✅ 진행도 {count/len(user_names)*100}%.... 중간 결과 저장 완료")

            

    # ✅ 브라우저 종료
    browser.close()

# ✅ 결과를 DataFrame으로 저장
user_data_zloa_df = pd.DataFrame(user_data_zloa, columns=['user_name', 'user_zloa_score'])
user_data_zloa_df.to_csv("user_data_zloa_df.csv", index=False, encoding="utf-8-sig")
print("✅ 결과 저장 완료")
