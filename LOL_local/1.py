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
    ward_placements = []  # 와드 설치 내역

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

        # 이벤트 처리
        for event in frame['events']:
            event_time = event['timestamp'] // 1000

            # 🗡️ 챔피언 킬 정보
            if event['type'] == 'CHAMPION_KILL':
                killer_id = event.get('killerId')
                assisting_ids = event.get('assistingParticipantIds', [])
                position = event.get('position', {})  # 안전하게 position 가져오기
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

            # 👁️ 와드 설치 이벤트
            if event['type'] == 'WARD_PLACED' and event.get('creatorId') == participant_id:
                position = event.get('position', {})
                x, y = position.get('x', None), position.get('y', None)
                ward_type = event.get('wardType', 'UNKNOWN')  # Control_Ward, Stealth_Ward 등

                if x is not None and y is not None:
                    ward_placements.append({
                        'time': event_time,
                        'x': x,
                        'y': y,
                        'wardType': ward_type
                    })

    # DataFrame 변환 및 정렬
    positions_df = pd.DataFrame(positions).sort_values('time').reset_index(drop=True)

    # ✅ 비어있는 경우 처리 추가
    if ward_placements:
        wards_df = pd.DataFrame(ward_placements).sort_values('time').reset_index(drop=True)
    else:
        wards_df = pd.DataFrame(columns=['time', 'x', 'y', 'wardType'])

    return positions_df, wards_df



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




if __name__ == "__main__":
    game_name = "행운을 빌어"
    tag_line = "wjsn"

    target_puuid = get_puuid(game_name, tag_line)
    match_id = get_recent_matches(target_puuid)

    match_id = match_id[10]

    match_details = get_match_details(match_id)
    if match_details:
        player_info = get_player_info(match_details, target_puuid)
        if player_info:
            team_id = player_info.get('teamId', 100)
            print(f"유저 정보:\n{player_info}")

            timeline_data = get_match_timeline(match_id)
            if timeline_data:
                positions_df, wards_df = extract_detailed_positions(timeline_data, player_info['participantId'])
                print("\n위치 정보 (시간별):")
                print(positions_df)

                print("\n와드 설치 내역:")
                print(wards_df)

                plot_maker(positions_df, wards_df, player_info, map_img, team_id)
            else:
                print("타임라인 정보를 불러오지 못했습니다.")
        else:
            print("유저 정보를 찾을 수 없습니다.")
    else:
        print("매치 정보를 불러오지 못했습니다.")


def debug_timeline_events(timeline_data):
    all_event_types = set()

    for frame in timeline_data['info']['frames']:
        for event in frame['events']:
            event_type = event.get('type', 'UNKNOWN')
            all_event_types.add(event_type)

    print("📋 모든 이벤트 타입:")
    for etype in sorted(all_event_types):
        print(f" - {etype}")

# 사용 예시
timeline_data = get_match_timeline(match_id)
debug_timeline_events(timeline_data)
