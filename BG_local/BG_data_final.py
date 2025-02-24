import aiohttp
import asyncio
import pandas as pd
import sys
import random


class PUBGAPI:
    def __init__(self, api_key, platform="steam"):
        """ PUBG API 클래스 초기화 """
        self.api_key = api_key
        self.platform = platform
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json"
        }
        self.semaphore = asyncio.Semaphore(20)  # 동시 요청 개수 제한
        self.telemetry_urls = {}  # ✅ Telemetry URL 저장
        self.telemetry_data = {}  # ✅ Telemetry 데이터 저장

    async def run_async_tasks(self, match_ids):
        async with aiohttp.ClientSession() as session:
            await self.get_telemetry_urls(session, match_ids)
            await self.get_telemetry_data(session)

    async def get_telemetry_urls(self, session, match_ids):
        tasks = [self.fetch_match_data(session, match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        self.telemetry_urls = {match_id: url for match_id, url in results if url is not None}

    async def get_telemetry_data(self, session):
        if not self.telemetry_urls:
            print("❌ Telemetry URL 데이터가 없습니다!")
            return

        tasks = [self.fetch_telemetry_data(session, url) for url in self.telemetry_urls.values()]
        results = await asyncio.gather(*tasks)
        self.telemetry_data = {match_id: data for match_id, data in zip(self.telemetry_urls.keys(), results) if data is not None}

    async def fetch_match_data(self, session, match_id):
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
        if not telemetry_url:
            return None

        retries = 0
        while retries < max_retries:
            try:
                async with self.semaphore:
                    async with session.get(telemetry_url, timeout=30) as response: 
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


# 🔹 CSV 파일에서 match_id 리스트 로드
df = pd.read_csv("match_id_list.csv")
match_id = df["match_id"].tolist()

match_id=random.sample(match_id,30)

# 🔹 PUBG API 클래스 인스턴스 생성
PUBG = PUBGAPI(api_key)
# 🔹 ✅ 하나의 asyncio.run()에서 모든 작업 실행
asyncio.run(PUBG.run_async_tasks(match_id))

# 🔹 CSV로 저장
PUBG.save_telemetry_urls("random3_telemetry_urls.csv")
PUBG.save_telemetry_data("random3_telemetry_data.json")