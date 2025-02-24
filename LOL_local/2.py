#%%

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cairosvg
from io import BytesIO
from PIL import Image
from matplotlib import rcParams

rcParams['font.family'] = 'Malgun Gothic'  # Windows 사용자
rcParams['axes.unicode_minus'] = False

# API KEY 설정
API_KEY = "RGAPI-258f98e4-61f1-4943-87d5-ce263367c83a"
HEADERS = {
    "X-Riot-Token": API_KEY
}

# SVG 파일을 PNG 이미지로 변환하는 함수
def svg_to_png_image(svg_path, zoom=0.5):
    png_data = cairosvg.svg2png(url=svg_path)
    image = Image.open(BytesIO(png_data))
    return OffsetImage(image, zoom=zoom)

# 에픽 몬스터 아이콘 로드
epic_monster_icons = {
    'DRAGON': svg_to_png_image('dragon.svg'),
    'BARON_NASHOR': svg_to_png_image('Baron.svg', zoom=0.1),
    'RIFTHERALD': svg_to_png_image('rift_herald.svg'),
    'VOIDGRUB': svg_to_png_image('voidgrub.svg')
}

map_img = mpimg.imread('map.png')

# 1. Riot ID → PUUID 조회
def get_puuid(game_name, tag_line, region="asia"):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("puuid", None)

# 2. PUUID → 최근 매치 리스트 조회
def get_recent_matches(puuid, region="asia", count=20):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# Match Details API 호출
def get_match_details(match_id, region="asia"):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match details: {response.status_code}")
        return None

# Match Timeline API 호출
def get_match_timeline(match_id, region="asia"):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching match timeline: {response.status_code}")
        return None

# 플레이어 정보 추출
def get_player_info(match_details, target_puuid):
    participants = match_details['info']['participants']
    game_mode = match_details['info'].get('gameMode', 'UNKNOWN')
    game_type = match_details['info'].get('gameType', 'UNKNOWN')
    queue_id = match_details['info'].get('queueId', 'UNKNOWN')

    for player in participants:
        if player['puuid'] == target_puuid:
            player_info = {
                'participantId': player['participantId'],
                'summonerName': player['summonerName'],
                'championName': player['championName'],
                'teamPosition': player.get('teamPosition', 'UNKNOWN'),
                'individualPosition': player.get('individualPosition', 'UNKNOWN'),
                'gameMode': game_mode,
                'gameType': game_type,
                'queueId': queue_id,
                'teamId': player.get('teamId', 'UNKNOWN') 
            }
            return player_info
    return None

def extract_detailed_positions(timeline_data, participant_id):
    positions = []
    ward_placements = []  # 필터링된 와드
    raw_ward_events = []  # 원본 와드 이벤트

    valid_ward_types = ['YELLOW_TRINKET', 'CONTROL_WARD', 'SIGHT_WARD', 'BLUE_TRINKET', 'STEALTH_WARD']

    for frame in timeline_data['info']['frames']:
        timestamp = frame['timestamp'] // 1000

        # 기본 위치 정보
        participant_frame = frame['participantFrames'].get(str(participant_id))
        if participant_frame and 'position' in participant_frame:
            positions.append({
                'time': timestamp,
                'x': participant_frame['position']['x'],
                'y': participant_frame['position']['y'],
                'source': 'frame'
            })

        for event in frame['events']:
            event_time = event['timestamp'] // 1000

            # 챔피언 킬 이벤트
            if event['type'] == 'CHAMPION_KILL':
                killer_id = event.get('killerId')
                assisting_ids = event.get('assistingParticipantIds', [])
                position = event.get('position', {})
                x, y = position.get('x', None), position.get('y', None)

                if x is not None and y is not None:
                    if killer_id == participant_id:
                        kill_type = 'Solo Kill' if not assisting_ids else 'Assisted Kill'
                    elif participant_id in assisting_ids:
                        kill_type = 'Assist'
                    else:
                        kill_type = None

                    if kill_type:
                        positions.append({
                            'time': event_time,
                            'x': x,
                            'y': y,
                            'source': kill_type
                        })

            # 👁️ 와드 설치 이벤트 (원본 이벤트 수집)
            if event['type'] == 'WARD_PLACED':
                # position 필드가 없는 경우 빈 딕셔너리 추가
                event_with_position = event.copy()
                if 'position' not in event_with_position:
                    event_with_position['position'] = {}

                raw_ward_events.append(event_with_position)

                creator_id = event.get('creatorId')
                ward_type = event.get('wardType', 'UNKNOWN')
                position = event.get('position', {})

                # 필터링된 와드
                if (creator_id == participant_id and
                    ward_type in valid_ward_types and
                    position):
                    x, y = position.get('x', None), position.get('y', None)
                    if x is not None and y is not None:
                        ward_placements.append({
                            'time': event_time,
                            'x': x,
                            'y': y,
                            'wardType': ward_type
                        })

    # 데이터프레임 변환
    positions_df = pd.DataFrame(positions).sort_values('time').reset_index(drop=True)
    wards_df = pd.DataFrame(ward_placements).drop_duplicates(subset=['time', 'x', 'y', 'wardType']).reset_index(drop=True)
    raw_wards_df = pd.DataFrame(raw_ward_events)

    # ✅ 원본 와드 이벤트 출력 (존재하는 컬럼만 출력)
    print("\n🔍 원본 와드 이벤트 (정제 전):")
    columns_to_display = [col for col in ['creatorId', 'timestamp', 'wardType', 'position'] if col in raw_wards_df.columns]
    print(raw_wards_df[columns_to_display])

    return positions_df, wards_df, raw_wards_df


# 위치 및 와드 시각화
def plot_maker(positions_df, wards_df, player_info, map_img, team_id):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(map_img, extent=[0, 15000, 0, 15000])

    # 이동경로 
    x = positions_df['x']
    y = positions_df['y']
    time = positions_df['time'] / 60 
    source = positions_df['source']

    cmap = plt.colormaps.get_cmap('viridis')
    kill_events = ['Solo Kill', 'Assisted Kill', 'Assist']
    is_kill = source.isin(kill_events)

    sc = ax.scatter(x[~is_kill], y[~is_kill], c=time[~is_kill], cmap=cmap, s=50, edgecolors='k')
    ax.scatter(x[is_kill], y[is_kill], color='red', s=80, edgecolors='k', label='Kill')
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Time (min)')

    # 와드
    for idx, ward in wards_df.iterrows():
        if ward['wardType'] == 'CONTROL_WARD':
            ax.scatter(ward['x'], ward['y'], c='magenta', marker='D', s=100, label='Control Ward' if idx == 0 else "")
        else:
            ax.scatter(ward['x'], ward['y'], c='cyan', marker='o', s=60, label='Stealth Ward' if idx == 0 else "")

    # 팀 이름
    team_name = 'Blue Team' if team_id == 100 else 'Red Team'
    ax.set_title(f"User : {player_info['summonerName']} Champion : ({player_info['championName']})\n{team_name}")

    # 설정
    ax.set_xlim(0, 15000)
    ax.set_ylim(0, 15000)
    ax.legend()
    ax.grid(True)
    plt.show()



def display_raw_ward_events(timeline_data):
    """
    타임라인 데이터에서 WARD_PLACED 이벤트를 필터링 없이 그대로 출력하는 함수.
    """
    raw_ward_events = []

    for frame in timeline_data['info']['frames']:
        for event in frame['events']:
            if event['type'] == 'WARD_PLACED':
                raw_ward_events.append(event)

    # 출력
    print("\n🔍 원본 WARD_PLACED 이벤트 (필터링 없이):")
    for event in raw_ward_events:
        print(event)

    print(f"\n총 와드 이벤트 수: {len(raw_ward_events)}")




if __name__ == "__main__":
    game_name = "행운을 빌어"
    tag_line = "wjsn"

    target_puuid = get_puuid(game_name, tag_line)
    match_id = get_recent_matches(target_puuid)

    match_id = match_id[0]  # 예시로 첫 번째 매치 사용

    match_details = get_match_details(match_id)
    if match_details:
        player_info = get_player_info(match_details, target_puuid)
        if player_info:
            team_id = player_info.get('teamId', 100)
            print(f"유저 정보:\n{player_info}")

            timeline_data = get_match_timeline(match_id)
            if timeline_data:
                # ⚡ 원본 WARD_PLACED 이벤트 출력
                display_raw_ward_events(timeline_data)
            else:
                print("타임라인 정보를 불러오지 못했습니다.")
        else:
            print("유저 정보를 찾을 수 없습니다.")
    else:
        print("매치 정보를 불러오지 못했습니다.")

# %%
