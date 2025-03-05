import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


post_data=pd.DataFrame(columns=['title', 'content', 'comments'])


headers = {"User-Agent": "Mozilla/5.0"}

def post_num_date_10chu(page_count):
    data = []
    # 페이지별 크롤링
    for i in range(page_count):
        # 크롤링할 URL
        url = f"https://www.inven.co.kr/board/lostark/6271?my=chu&p={i+1}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select("tr.lgtm")
        for row in rows:
            # 게시글 번호/  날짜 
            post_number = row.select_one("td.num").get_text(strip=True)
            post_date = row.select_one("td.date").get_text(strip=True)
            # 데이터 저장
            data.append({"post_num": post_number, "post_date": post_date})

    # pandas DataFrame으로 변환
    post_num_df = pd.DataFrame(data)
    return post_num_df

def post_num_date_30chu(page_count):
    data = []
    for i in range(page_count):

        url = f"https://www.inven.co.kr/board/lostark/6271?my=chuchu&p={i+1}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')


        rows = soup.select("tr.lgtm")
        for row in rows:
            # 게시글 번호와 날짜 추출
            post_number = row.select_one("td.num").get_text(strip=True)
            post_date = row.select_one("td.date").get_text(strip=True)
            # 데이터 저장
            data.append({"post_num": post_number, "post_date": post_date})



    post_num_30_df = pd.DataFrame(data)
    return post_num_30_df

def crawl_inven_post(post_num):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')                 # Headless 모드
    options.add_argument('--disable-dev-shm-usage')    # 공유 메모리 비활성화
    options.add_argument('--no-sandbox')               # 샌드박스 비활성화
    options.add_argument('--disable-gpu') 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = f"https://www.inven.co.kr/board/lostark/6271/{post_num}?my=chu"
        driver.get(url)

        # WebDriverWait으로 요소 대기
        wait = WebDriverWait(driver, 10)  # 최대 10초 대기

        # 제목 
        try:
            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.articleTitle > h1")))
            title = title_elem.text.strip()
        except:
            title = ""

        # 본문 
        try:
            content_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#powerbbsContent")))
            content = content_elem.text.strip()
        except:
            content = ""

        # 댓글 << javascript 때문에 가져오기 힘들다..
        comments = []
        try:
            comment_elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.comment > span.content.cmtContentOne")))
            for elem in comment_elems:
                comments.append(elem.text.strip())
        except:
            comments = []

        return {
            "title": title,
            "content": content,
            "comments": comments
        }

    finally:
        driver.quit()


#댓글-대댓글 분류
def comment_sp(c):
  threaded_comments = []
  current_parent = None

  for cmt in c:
      if cmt.startswith('@'):
          # (a) '@'로 시작 → '대댓글(답글)'로 처리
          # current_parent가 None이 아닐 때만 replies에 추가
          if current_parent is not None:
              current_parent["replies"].append(cmt)
          else:
              # 만약 첫 댓글부터 '@'로 시작한다면?
              # 특별히 처리하지 않거나, 필요하면 아래처럼 "알 수 없는 부모"에 넣을 수도 있음
              # pass
              # 예시: 그냥 새 parent로 간주하지 않고 무시
              pass
      else:
          # (b) '@'로 시작하지 않으면 '새 부모' 댓글
          parent_block = {
              "Main": cmt,
              "replies": []
          }
          threaded_comments.append(parent_block)
          current_parent = parent_block
  return threaded_comments


# 최종 df만들기
def make_post(post_num):
  global post_data
  for i in post_num:
    data = crawl_inven_post(i)
    temp_data = {
            'title': data['title'],
            'content': data['content'],
            'comments': comment_sp(data['comments'])
        }
 
    post_data = pd.concat([post_data, pd.DataFrame([temp_data])], ignore_index=True)



post_nums = post_num_date_10chu(5)["post_num"].tolist()

make_post(post_nums)

file_path = "post_data.csv"

# DataFrame 저장
post_data.to_csv(file_path, index=False, encoding="utf-8-sig")

print(f"데이터가 '{file_path}'에 저장되었습니다.")



