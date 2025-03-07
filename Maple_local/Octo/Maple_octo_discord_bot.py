import discord
from discord.ext import commands
import numpy as np
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

token_key = os.getenv("TOKEN_KEY")



intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)


def prob_setting_B(n):
    # 1~8단계 확률
    prob_table = {
        1: (1.00, 0.00, 0.00),
        2: (0.60, 0.00, 0.00),  # 2단계는 실패해도 단계 유지
        3: (0.50, 0.50, 0.00),
        4: (0.40, 0.60, 0.00),
        5: (0.307, 0.693, 0.00),
        6: (0.205, 0.765, 0.03),
        7: (0.103, 0.857, 0.04),
        8: (0.05,  0.90,  0.05),
    }

    T = np.zeros((n+1, n+1))

    for lvl in range(1,n):
        i = lvl
        p_s, p_f, p_r = prob_table[lvl]

        T[i, i-1] = p_f # 실패
        T[i, 0]    = p_r # 도망
        
        if lvl < n-1:  # 1 to n-2 단계
            T[i, i+2] = p_s * 0.05  # 대성공 
            T[i, i+1] = p_s * 0.95  # 성공
        else:          # n-1 단계
            T[i, i+1] = p_s        # 성공

    # 0, n 단계는 흡수상태
    T[0,0] = 1 
    T[n,n] = 1

    # 2단계에서 실패해도 단계 유지
    T[2,2] = 0.4

    return T


def octo_prob(now, goal, now_count):
    """
    now      : 현재 강화 단계
    goal     : 목표 단계
    now_count: 현재 몇 번 시도했는지 (전체 100번까지만 가능하게 가정)
    """
    # 예외처리
    if now >= goal:
        return "현재 단계보다 높은 목표를 설정하세요."
    elif goal > 9:
        return "9단계 이하로만 설정 가능합니다."
    elif now_count >= 100:
        return "문어가 밥을 다 먹었습니다. 내일 다시 시도하세요."

    p = np.zeros(goal+1)
    p[now] = 1

    T = prob_setting_B(goal)
    T_n = np.linalg.matrix_power(T, 100 - now_count)

    octo = p @ T_n

    result_lines = []
    for lvl, prob in enumerate(octo):
        result_lines.append(f"{lvl}단계 : {prob*100:.4f}%")
    return "\n".join(result_lines)





@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")




@bot.command(name="문어")
async def octo(ctx, now: int, goal: int, now_count: int):
    result = octo_prob(now, goal, now_count)
    await ctx.send(result)



bot.run(token_key)
