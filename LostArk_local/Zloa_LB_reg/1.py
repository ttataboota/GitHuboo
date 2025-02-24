from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]

    # ✅ 페이지 제목 출력
    print("✅ 현재 페이지 제목:", page.title())

    # ✅ 로딩 스피너가 사라질 때까지 대기
    try:
        page.wait_for_selector("div.loading-spinner", state="hidden", timeout=60000)
        print("✅ 로딩 완료")
    except Exception as e:
        print("⚠️ 로딩 스피너를 찾지 못했거나 시간 초과:", e)

    try:
        # "캐릭터 이름" th 태그가 있는 tr에서 td를 추출
        character_selector = "tr:has(th:text('캐릭터 이름')) td"
        page.wait_for_selector(character_selector, timeout=10000)
        character_element = page.query_selector(character_selector)

        if character_element:
            character_name = character_element.inner_text()
            print(f"🎮 캐릭터 이름: {character_name}")
        else:
            print("❌ 캐릭터 이름을 찾지 못했습니다.")

    except Exception as e:
        print("❌ 캐릭터 이름 추출 중 오류 발생:", e)

    # ✅ 최고 환산 점수 추출
    try:
        # "최고 환산 점수" 텍스트가 있는 <th>를 찾고, 그에 맞는 <td> 값 추출
        highest_score_selector = "tr:has(th:text('최고 환산 점수')) td"
        page.wait_for_selector(highest_score_selector, timeout=10000)
        highest_score_element = page.query_selector(highest_score_selector)
        
        if highest_score_element:
            highest_score = highest_score_element.inner_text()
            print(f"🏆 최고 환산 점수: {highest_score}")
        else:
            print("❌ 최고 환산 점수를 찾지 못했습니다.")
    except Exception as e:
        print("❌ 최고 환산 점수 추출 중 오류 발생:", e)


    # ✅ 브라우저 종료 (필요 시 주석 처리 가능)
    browser.close()


