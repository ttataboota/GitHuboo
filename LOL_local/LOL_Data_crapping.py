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

API_KEY = "RGAPI-258f98e4-61f1-4943-87d5-ce263367c83a"
HEADERS = {
    "X-Riot-Token": API_KEY
}

# SVG>PNG
def svg_to_png_image(svg_path, zoom=0.5):
    png_data = cairosvg.svg2png(url=svg_path)
    image = Image.open(BytesIO(png_data))
    return OffsetImage(image, zoom=zoom)



epic_monster_icons = {
    'DRAGON': svg_to_png_image('dragon.svg'),
    'BARON_NASHOR': svg_to_png_image('Baron.svg', zoom=0.1),
    'RIFTHERALD': svg_to_png_image('rift_herald.svg'),
    'VOIDGRUB': svg_to_png_image('voidgrub.svg')
}

map_img = mpimg.imread('map.png')

# 닉네임 + 태그 >> puuid 
def get_puuid(game_name, tag_line, region="asia"):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("puuid", None)

# puuid >> matchid
def get_recent_matches(puuid, region="asia", count=20):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# matchid >> match_data
def get_match_details(match_id, region="asia"):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()

# matchid >> timeline_data
def get_match_timeline(match_id, region="asia"):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()


#유저정보
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


#기본 위치 + 특수 조건에 의해 위치 기록되는거 추가
def extract_detailed_positions(timeline_data, participant_id):
    positions = []
    epic_monster_kills = []  

    for frame in timeline_data['info']['frames']:
        timestamp = frame['timestamp'] // 1000 

        participant_frame = frame['participantFrames'].get(str(participant_id))
        if participant_frame and 'position' in participant_frame:
            positions.append({
                'time': timestamp,
                'x': participant_frame['position']['x'],
                'y': participant_frame['position']['y'],
                'source': 'frame'
            })
        for event in frame['events']:
            # 솔로킬 / 일반 킬 / 어시 구분
            if event['type'] == 'CHAMPION_KILL':
                killer_id = event.get('killerId')
                assisting_ids = event.get('assistingParticipantIds', [])
                # victim_id = event.get('victimId')
                event_time = event['timestamp'] // 1000
                x, y = event['position']['x'], event['position']['y']

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

    positions_df = pd.DataFrame(positions).sort_values('time').reset_index(drop=True)


    # 에픽몬스터 잡힐 시간과 가장 가까운 시간에 유저 위치
    for frame in timeline_data['info']['frames']:
        for event in frame['events']:
            if event['type'] == 'ELITE_MONSTER_KILL':
                monster_type = event.get('monsterType')
                event_time = event['timestamp'] // 1000



                closest_idx = (positions_df['time'] - event_time).abs().idxmin()
                closest_position = positions_df.loc[closest_idx]

                epic_monster_kills.append({
                    'time': event_time,
                    'x': closest_position['x'],  
                    'y': closest_position['y'],
                    'monsterType': monster_type
                })

    epic_monsters_df = pd.DataFrame(epic_monster_kills) 

    return positions_df, epic_monsters_df



def plot_maker(positions_df, player_info, map_img, team_id, epic_monsters_df):
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


    for _, row in epic_monsters_df.iterrows():
        monster_type = row['monsterType']
        x, y = row['x'], row['y']
        event_time = row['time'] / 60 

        if monster_type in epic_monster_icons:
            ab = AnnotationBbox(epic_monster_icons[monster_type], (x, y), frameon=False)
            ax.add_artist(ab)
            ax.text(x, y + 300, monster_type, color='white', fontsize=8, ha='center')

            cbar_ax = cbar.ax
            y_pos = event_time 

            cbar_ab = AnnotationBbox(
                epic_monster_icons[monster_type],
                (-0.15, y_pos),  
                xycoords=('axes fraction', 'data'), 
                frameon=False,
                box_alignment=(0, 0.5)
            )
            cbar_ax.add_artist(cbar_ab)

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
    game_name = "소환사있다"
    tag_line = "KR1"

    target_puuid = get_puuid(game_name, tag_line)
    match_id = get_recent_matches(target_puuid)

    match_id = match_id[1]

    match_details = get_match_details(match_id)
    if match_details:
        player_info = get_player_info(match_details, target_puuid)
        if player_info:
            team_id = player_info.get('teamId', 100)
            print(f"유저 정보 : {player_info}")

            timeline_data = get_match_timeline(match_id)
            if timeline_data:
                positions_df, epic_monsters_df = extract_detailed_positions(timeline_data, player_info['participantId'])
                print("위치 정보 (min):")
                print(positions_df)

                plot_maker(positions_df, player_info, map_img, team_id, epic_monsters_df)
        else:
            print("유저 정보 x")
    else:
        print("매치 정보 x")
