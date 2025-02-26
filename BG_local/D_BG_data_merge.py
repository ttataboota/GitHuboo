#%%

import pandas as pd
import numpy as np
import math
from functools import reduce

telemetry_data=pd.read_json("random3_telemetry_data.json",lines=True)
telemetry_data=telemetry_data['data']






def get_user_name(telemetry_data):
    user_name=[]
    for telemetry_data_part in telemetry_data:
        for event in telemetry_data_part:
            if event["_T"] == "LogPlayerTakeDamage":
                if event.get("attacker")!=None:
                    attacker = event.get("attacker")
                    attacker_name=attacker.get('name')
                    user_name.append(attacker_name)


    user_name=list(set(user_name))
    return user_name


logplayerattack_weapon_dict = {
    # 🔹 돌격소총 (AR)
    "WeapAK47_C": "AKM",
    "WeapM16A4_C": "M16A4",
    "WeapSCAR-L_C": "SCAR-L",
    "WeapHK416_C": "M416",
    "WeapAUG_C": "AUG",
    "WeapGroza_C": "Groza",
    "WeapQBZ95_C": "QBZ95",
    "WeapBerylM762_C": "Beryl M762",
    "WeapG36C_C": "G36C",
    "WeapMk47Mutant_C": "Mk47 Mutant",
    "WeapK2_C": "K2",
    "WeapACE32_C": "ACE32",
    "WeapFAMAS_C": "FAMAS",  # 최신 무기 추가

    # 🔹 지정사수소총 (DMR)
    "WeapSKS_C": "SKS",
    "WeapMini14_C": "Mini14",
    "WeapSLR_C": "SLR",
    "WeapMk14_C": "Mk14",
    "WeapQBU88_C": "QBU",
    "WeapVSS_C": "VSS",
    "WeapMk12_C": "Mk12",  # 최신 무기 추가

    # 🔹 저격소총 (SR)
    "WeapKar98k_C": "Kar98k",
    "WeapM24_C": "M24",
    "WeapAWM_C": "AWM",
    "WeapWin94_C": "Win94",
    "WeapMosinNagant_C": "Mosin Nagant",  # 최신 무기 추가

    # 🔹 기관단총 (SMG)
    "WeapUZI_C": "Micro UZI",
    "WeapUMP_C": "UMP45",
    "WeapVector_C": "Vector",
    "WeapThompson_C": "Thompson",
    "WeapMP5K_C": "MP5K",
    "WeapPP19Bizon_C": "PP-19 Bizon",
    "WeapP90_C": "P90",  # 최신 무기 추가

    # 🔹 경기관총 (LMG)
    "WeapDP28_C": "DP-28",
    "WeapM249_C": "M249",
    "WeapMG3_C": "MG3",  # 최신 무기 추가

    # 🔹 샷건 (SG)
    "WeapS1897_C": "S1897",
    "WeapS686_C": "S686",
    "WeapS12K_C": "S12K",
    "WeapSawnoff_C": "Sawed-off",
    "WeapDBS_C": "DBS",
    "WeapM1014_C": "M1014",  # 최신 무기 추가

    # 🔹 권총 (Pistol)
    "WeapM1911_C": "P1911",
    "WeapM9_C": "P92",
    "WeapRhino_C": "R45",
    "WeapNagantM1895_C": "R1895",
    "WeapG18_C": "P18C",
    "WeapSkorpion_C": "Skorpion",

    # 🔹 근접 무기 (Melee)
    "WeapPan_C": "Pan",
    "WeapMachete_C": "Machete",
    "WeapCrowbar_C": "Crowbar",
    "WeapSickle_C": "Sickle",

    # 🔹 활과 석궁
    "WeapCrossbow_1_C": "Crossbow",

    # 🔹 투척 무기 (Throwables)
    "ProjGrenade_C": "Frag Grenade",
    "ProjMolotov_C": "Molotov Cocktail",
    "ProjSmokeBomb_C": "Smoke Grenade",
    "ProjFlashBang_C": "Flashbang",

    # 🔹 차량 (Vehicles)
    "Uaz_A_01_C": "UAZ",
    "Dacia_A_01_C": "Dacia",
    "Motorbike_01_C": "Motorbike",
    "Buggy_A_01_C": "Buggy",
    "Boat_PG117_C": "Boat",

    # 🔹 환경적 피해 (Environmental Damage)
    "BlueZoneDamageField": "Blue Zone",
    "RedZoneBomb_C": "Red Zone",
    "BP_MolotovFireDebuff_C": "Molotov Fire",
    "BP_KillTruck_C": "Kill Truck"
}
logplayertakedamage_weapon_dict = {
    # 🔹 돌격소총 (AR)
    "Item_Weapon_AK47_C": "AKM",
    "Item_Weapon_M16A4_C": "M16A4",
    "Item_Weapon_SCAR-L_C": "SCAR-L",
    "Item_Weapon_HK416_C": "M416",
    "Item_Weapon_M416_C": "M416",
    "Item_Weapon_AUG_C": "AUG",
    "Item_Weapon_Groza_C": "Groza",
    "Item_Weapon_QBZ95_C": "QBZ95",
    "Item_Weapon_BerylM762_C": "Beryl M762",
    "Item_Weapon_G36C_C": "G36C",
    "Item_Weapon_Mk47Mutant_C": "Mk47 Mutant",
    "Item_Weapon_K2_C": "K2",
    "Item_Weapon_ACE32_C": "ACE32",
    "Item_Weapon_FAMAS_C": "FAMAS",  # 최신 무기 추가

    # 🔹 지정사수소총 (DMR)
    "Item_Weapon_SKS_C": "SKS",
    "Item_Weapon_Mini14_C": "Mini14",
    "Item_Weapon_SLR_C": "SLR",
    "Item_Weapon_Mk14_C": "Mk14",
    "Item_Weapon_QBU88_C": "QBU",
    "Item_Weapon_VSS_C": "VSS",
    "Item_Weapon_Mk12_C": "Mk12",  # 최신 무기 추가

    # 🔹 저격소총 (SR)
    "Item_Weapon_Kar98k_C": "Kar98k",
    "Item_Weapon_M24_C": "M24",
    "Item_Weapon_AWM_C": "AWM",
    "Item_Weapon_Win94_C": "Win94",
    "Item_Weapon_MosinNagant_C": "Mosin Nagant",  # 최신 무기 추가

    # 🔹 기관단총 (SMG)
    "Item_Weapon_UZI_C": "Micro UZI",
    "Item_Weapon_UMP_C": "UMP45",
    "Item_Weapon_Vector_C": "Vector",
    "Item_Weapon_Thompson_C": "Thompson",
    "Item_Weapon_MP5K_C": "MP5K",
    "Item_Weapon_PP19Bizon_C": "PP-19 Bizon",
    "Item_Weapon_P90_C": "P90",  # 최신 무기 추가

    # 🔹 경기관총 (LMG)
    "Item_Weapon_DP28_C": "DP-28",
    "Item_Weapon_M249_C": "M249",
    "Item_Weapon_MG3_C": "MG3",  # 최신 무기 추가

    # 🔹 샷건 (SG)
    "Item_Weapon_S1897_C": "S1897",
    "Item_Weapon_S686_C": "S686",
    "Item_Weapon_S12K_C": "S12K",
    "Item_Weapon_Sawnoff_C": "Sawed-off",
    "Item_Weapon_DBS_C": "DBS",
    "Item_Weapon_M1014_C": "M1014",  # 최신 무기 추가

    # 🔹 권총 (Pistol)
    "Item_Weapon_M1911_C": "P1911",
    "Item_Weapon_P92_C": "P92",
    "Item_Weapon_Rhino_C": "R45",
    "Item_Weapon_NagantM1895_C": "R1895",
    "Item_Weapon_P18C_C": "P18C",
    "Item_Weapon_Skorpion_C": "Skorpion",

    # 🔹 근접 무기 (Melee)
    "Item_Weapon_Pan_C": "Pan",
    "Item_Weapon_Machete_C": "Machete",
    "Item_Weapon_Crowbar_C": "Crowbar",
    "Item_Weapon_Sickle_C": "Sickle",

    # 🔹 활과 석궁
    "Item_Weapon_Crossbow_C": "Crossbow",

    # 🔹 투척 무기 (Throwables)
    "Item_Weapon_Grenade_C": "Frag Grenade",
    "Item_Weapon_Molotov_C": "Molotov Cocktail",
    "Item_Weapon_SmokeBomb_C": "Smoke Grenade",
    "Item_Weapon_FlashBang_C": "Flashbang",

    # 🔹 차량 (Vehicles)
    "Item_Vehicle_UAZ_C": "UAZ",
    "Item_Vehicle_Dacia_C": "Dacia",
    "Item_Vehicle_Motorbike_C": "Motorbike",
    "Item_Vehicle_Buggy_C": "Buggy",
    "Item_Vehicle_Boat_C": "Boat",

    # 🔹 환경적 피해 (Environmental Damage)
    "Item_Environment_BlueZone": "Blue Zone",
    "Item_Environment_RedZone": "Red Zone",
    "Item_Environment_MolotovFire": "Molotov Fire",
    "Item_Environment_KillTruck": "Kill Truck"
}
hit_locations = [
    "HeadShot",   # 머리
    "NeckShot",   # 목
    "TorsoShot",  # 상체 (가슴, 복부 포함)
    "PelvisShot", # 골반
    "ArmShot",    # 팔 (어깨, 팔뚝 포함)
    "LegShot",     # 다리 (허벅지, 종아리, 발 포함)
    "NonSpecific" # 수류탄 류는 이런식으로 나옴
]

column_list=['fire_count','hit','wall_hit','distance(mean)','distance(max)','distance(min)']
column_list=column_list.extend(hit_locations)



def calculate_distance(loc1, loc2):
    return round((math.sqrt((loc2["x"] - loc1["x"])**2 + (loc2["y"] - loc1["y"])**2)/100),2)

def df_cleaner(df):
    pd.set_option('future.no_silent_downcasting', True)
    df.replace({"": np.nan, "[]": np.nan, "{}": np.nan, "None": np.nan}, inplace=True)
    df.dropna(inplace=True)
    df.replace(logplayerattack_weapon_dict,inplace=True)
    df.replace(logplayertakedamage_weapon_dict,inplace=True)



def data_merge(df_combat_1,df_combat_2):

    global hit_locations,column_list


    df_combat_1_count=df_combat_1.groupby('weapon',as_index=False)['fire_count'].max() 
    weapon_hits = df_combat_2[df_combat_2['damage'] > 0].groupby('weapon')['weapon'].count()
    df_combat_1_count['hit'] = round(df_combat_1_count['weapon'].map(weapon_hits).fillna(0)/df_combat_1_count['fire_count'],3)


    df_combat_wall_hit=df_combat_2.groupby(['weapon'])['damage'].agg(damage_0_rate=lambda x : (x==0).sum() / len(x) )


    df_combat_2_count=df_combat_2.groupby('weapon').agg({'distance(m)':['mean','min','max']})
    df_combat_2_count.columns = ['distance_mean', 'distance_min', 'distance_max']
    df_combat_2_count = df_combat_2_count.reset_index()


    df_summary = df_combat_2.groupby(['weapon', 'damage_reason']).size().unstack(fill_value=0)
    df_summary = df_summary.reindex(columns=hit_locations, fill_value=0).reset_index()
    df_summary = df_summary.rename_axis(None, axis=1)



    df_list = [df_combat_1_count, df_combat_wall_hit, df_combat_2_count, df_summary]
    df_data = reduce(lambda left, right: pd.merge(left, right, on='weapon', how='left'), df_list)

    df_data.dropna(inplace=True)

    return df_data



def get_BG_data(telemetry_data,user_name):


    data=[]

    for telemetry_data_part in telemetry_data:
        for TARGET_PLAYER in user_name:

            combat_logs_1 = []
            combat_logs_2 = []
            for event in telemetry_data_part:
                # 🔹 공격 이벤트 (LogPlayerAttack)
                if event["_T"] == "LogPlayerAttack":
                    attacker = event.get("attacker")
                    if attacker and attacker.get("name") == TARGET_PLAYER: 
                        combat_logs_1.append({
                            "time": event["_D"],
                            "weapon": event.get("weapon", {}).get("itemId", "Unknown"),
                            "fire_count": event['fireWeaponStackCount'],
                            
                            
                        })

                if event["_T"] == "LogPlayerTakeDamage":
                    attacker = event.get("attacker")
                    victim = event.get("victim")

                    if (attacker and attacker.get("name") == TARGET_PLAYER):
                        combat_logs_2.append({
                            "time": event["_D"],
                            "damage": event["damage"],
                            "damage_reason" : event['damageReason'],
                            "distance(m)": calculate_distance(event['attacker']['location'],event['victim']['location']),
                            "weapon": event['damageCauserName']
                        })

            df_combat_1 = pd.DataFrame(combat_logs_1)
            df_cleaner(df_combat_1)
            df_combat_2 = pd.DataFrame(combat_logs_2)
            df_cleaner(df_combat_2)


            if df_combat_1.empty or df_combat_2.empty:
                continue

            df_data=data_merge(df_combat_1,df_combat_2)

            df_data['player_name']=TARGET_PLAYER


            data.append(df_data)
    return data


data=get_BG_data(telemetry_data,get_user_name(telemetry_data))
data_all = pd.concat(data, ignore_index=True)  



data_all.to_csv("data/data_all_random3.csv", index=False)


#%%


