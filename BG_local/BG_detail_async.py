import aiohttp
import asyncio
import pandas as pd
import sys



class PUBGAPI:
    def __init__(self, api_key,telemetry_urls, platform="steam"):
        """ PUBG API 클래스 초기화 """
        self.api_key = api_key
        self.platform = platform
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json"
        }
        self.semaphore = asyncio.Semaphore(20)  # 동시 요청 개수 제한
        self.telemetry_urls = telemetry_urls  # ✅ Telemetry URL 저장
        self.telemetry_data = {}  # ✅ Telemetry 데이터 저장

    async def run_async_tasks(self):
        """ ✅ 모든 비동기 작업을 한 번의 이벤트 루프에서 실행 """
        async with aiohttp.ClientSession() as session:
            await self.get_telemetry_data(session)

    async def get_telemetry_urls(self, session, match_ids):
        """ 여러 Match ID에서 Telemetry URL을 비동기적으로 가져오는 함수 """
        tasks = [self.fetch_match_data(session, match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        self.telemetry_urls = {match_id: url for match_id, url in results if url is not None}

    async def get_telemetry_data(self, session):
        """ 여러 Telemetry URL에서 데이터를 가져오는 함수 """
        if not self.telemetry_urls:
            print("❌ Telemetry URL 데이터가 없습니다!")
            return

        tasks = [self.fetch_telemetry_data(session, url) for url in self.telemetry_urls.values()]
        results = await asyncio.gather(*tasks)
        self.telemetry_data = {match_id: data for match_id, data in zip(self.telemetry_urls.keys(), results) if data is not None}

    async def fetch_match_data(self, session, match_id):
        """ 특정 Match ID에서 Telemetry URL을 가져오는 함수 """
        url = f"https://api.pubg.com/shards/{self.platform}/matches/{match_id}"
        async with self.semaphore:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    match_data = await response.json()
                    telemetry_url = next(
                        (asset["attributes"]["URL"] for asset in match_data.get("included", []) if asset["type"] == "asset"),
                        None
                    )
                    return match_id, telemetry_url
                return match_id, None

    async def fetch_telemetry_data(self, session, telemetry_url, max_retries=3):
        """ 특정 Telemetry URL에서 데이터를 가져오는 함수 (오류 방지 & 자동 재시도) """
        if not telemetry_url:
            return None

        retries = 0
        while retries < max_retries:
            try:
                async with self.semaphore:
                    async with session.get(telemetry_url, timeout=30) as response:  # ✅ Timeout 추가 (30초)
                        if response.status == 200:
                            return await response.json()
                        else:
                            print(f"❌ Telemetry 데이터 요청 실패 - HTTP {response.status}")
                            return None
            except asyncio.TimeoutError:
                print(f"⚠️ 요청 시간이 초과되었습니다. {retries + 1}/{max_retries} 재시도 중...")
            except aiohttp.ClientError as e:
                print(f"⚠️ 네트워크 오류 발생: {e}. {retries + 1}/{max_retries} 재시도 중...")
            
            retries += 1
            await asyncio.sleep(5)  # ✅ 재시도 전 5초 대기

        print(f"❌ Telemetry 데이터 요청 실패: {telemetry_url}")
        return None

    def save_telemetry_urls(self, filename="telemetry_urls.csv"):
        """ ✅ Telemetry URL 데이터를 CSV 파일로 저장 """
        df = pd.DataFrame(self.telemetry_urls.items(), columns=["match_id", "telemetry_url"])
        df.to_csv(filename, index=False)
        print(f"✅ Telemetry URL 데이터 저장 완료: {filename}")

    def save_telemetry_data(self, filename="telemetry_data.json"):
        """ ✅ Telemetry 데이터를 JSON 파일로 저장 """
        if not self.telemetry_data:
            print("❌ 저장할 Telemetry 데이터가 없습니다!")
            return
        df = pd.DataFrame(self.telemetry_data.items(), columns=["match_id", "data"])
        df.to_json(filename, orient="records", lines=True)
        print(f"✅ Telemetry 데이터 저장 완료: {filename}")


api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJhMTA2NjVlMC0wMDI5LTAxM2ItMjE3MS0yNzQ4YzRhN2Q1ZDYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjYwNzIwMjQyLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii01NGI0MDRmMy1kZDFhLTQwMzItYWJlMC1mMGU5ZWE3NDQxNzUifQ.wNUumN93avLiYsfnAv3JAJycd4V2jcxWdFOzgqNmVcc'

df = pd.read_csv("telemetry_urls.csv")
df=df.head(10)
telemetry_urls= df.set_index("match_id")["telemetry_url"].to_dict()



# 🔹 PUBG API 클래스 인스턴스 생성
PUBG = PUBGAPI(api_key,telemetry_urls)



asyncio.run(PUBG.run_async_tasks())


# 🔹 CSV로 저장

PUBG.save_telemetry_data("telemetry_data.json")