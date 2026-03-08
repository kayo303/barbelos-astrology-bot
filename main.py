import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from dotenv import load_dotenv

from data import system_texts, element_texts, region_texts, weapon_texts

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN 이 설정되지 않았습니다.")

KST = ZoneInfo("Asia/Seoul")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def get_kst_now() -> datetime:
    return datetime.now(KST)


def get_kst_date_string() -> str:
    return get_kst_now().strftime("%Y-%m-%d")


def get_kst_display_date() -> str:
    return get_kst_now().strftime("%Y년 %m월 %d일")


def pick_random_entry(rng: random.Random, data_dict: dict):
    name = rng.choice(list(data_dict.keys()))
    text = rng.choice(data_dict[name])
    return name, text


def score_bar(score: int) -> str:
    filled = round(score / 10)
    filled = max(1, min(10, filled))
    empty = 10 - filled
    return f"{'✦' * filled}{'✧' * empty} `{score}`"


def get_score_comment(score: int) -> str:
    if score >= 90:
        return "매우 강한 흐름"
    if score >= 75:
        return "좋은 흐름"
    if score >= 60:
        return "무난한 흐름"
    if score >= 40:
        return "조심스러운 흐름"
    return "불안정한 흐름"


def build_overall_message(element_name: str, region_name: str, weapon_name: str, brightness: int) -> str:
    tone = ""
    if brightness >= 85:
        tone = "오늘의 별빛은 유난히 선명합니다. 직감이 가리키는 방향을 믿어도 좋습니다."
    elif brightness >= 65:
        tone = "별의 흐름이 비교적 안정적입니다. 차분히 움직이면 좋은 결과를 기대할 수 있습니다."
    elif brightness >= 40:
        tone = "별빛이 완전히 흐리지는 않지만, 서두름은 피하는 편이 좋겠습니다."
    else:
        tone = "오늘은 흐름이 다소 흔들립니다. 결정보다 관찰에 힘을 두는 편이 좋겠습니다."

    return (
        f"오늘의 별은 **{element_name}**의 결, **{region_name}**의 기운, "
        f"그리고 **{weapon_name}**의 징조를 함께 비추고 있습니다.\n"
        f"{tone}"
    )


def generate_astrology(user_id: int):
    kst_date = get_kst_date_string()
    rng = random.Random(f"{user_id}-{kst_date}")

    brightness = rng.randint(1, 100)

    element_name, element_text = pick_random_entry(rng, element_texts)
    region_name, region_text = pick_random_entry(rng, region_texts)
    weapon_name, weapon_text = pick_random_entry(rng, weapon_texts)

    study_score = rng.randint(1, 100)
    relationship_score = rng.randint(1, 100)
    soul_score = rng.randint(1, 100)
    wealth_score = rng.randint(1, 100)
    body_score = rng.randint(1, 100)
    wish_score = rng.randint(1, 100)

    overall = build_overall_message(
        element_name=element_name,
        region_name=region_name,
        weapon_name=weapon_name,
        brightness=brightness,
    )

    return {
        "kst_date": kst_date,
        "kst_display_date": get_kst_display_date(),
        "brightness": brightness,
        "element_name": element_name,
        "element_text": element_text,
        "region_name": region_name,
        "region_text": region_text,
        "weapon_name": weapon_name,
        "weapon_text": weapon_text,
        "study_score": study_score,
        "relationship_score": relationship_score,
        "soul_score": soul_score,
        "wealth_score": wealth_score,
        "body_score": body_score,
        "wish_score": wish_score,
        "overall": overall,
    }


def build_embed(result: dict, user_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=system_texts["title"],
        description=(
            f"별과 원소의 흐름을 따라, 오늘 **{user_name}**에게 닿는 징조를 읽어드립니다.\n"
        ),
        color=discord.Color.from_rgb(88, 72, 156),
    )

    embed.add_field(
        name="✦ 오늘의 별빛",
        value=(
            f"**별의 밝기 {result['brightness']}**\n"
            f"{score_bar(result['brightness'])}"
        ),
        inline=False,
    )

    embed.add_field(
        name="✦ 오늘의 원소",
        value=f"**{result['element_name']}**\n{result['element_text']}",
        inline=False,
    )
    embed.add_field(
        name="✦ 오늘의 지역",
        value=f"**{result['region_name']}**\n{result['region_text']}",
        inline=False,
    )
    embed.add_field(
        name="✦ 오늘의 무기",
        value=f"**{result['weapon_name']}**\n{result['weapon_text']}",
        inline=False,
    )

    embed.add_field(
        name="✦ 종합 점성 결과",
        value=result["overall"],
        inline=False,
    )

    flow_lines = [
        f"**학업의 흐름**  {score_bar(result['study_score'])} · {get_score_comment(result['study_score'])}",
        f"**관계의 흐름**  {score_bar(result['relationship_score'])} · {get_score_comment(result['relationship_score'])}",
        f"**영혼의 흐름**  {score_bar(result['soul_score'])} · {get_score_comment(result['soul_score'])}",
        f"**재물의 흐름**  {score_bar(result['wealth_score'])} · {get_score_comment(result['wealth_score'])}",
        f"**신체의 흐름**  {score_bar(result['body_score'])} · {get_score_comment(result['body_score'])}",
        f"**기원의 흐름**  {score_bar(result['wish_score'])} · {get_score_comment(result['wish_score'])}",
    ]

    embed.add_field(
        name="✦ 세부 흐름",
        value="\n".join(flow_lines),
        inline=False,
    )

    embed.set_footer(
        text=(
            f"{result['kst_display_date']} · KST 기준 "
            f"· {system_texts['footer']}"
        )
    )

    return embed


@bot.event
async def on_ready():
    print(f"로그인 완료: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 동기화 완료: {len(synced)}개")
    except Exception as e:
        print(f"동기화 실패: {e}")


@bot.tree.command(name="점성술", description="바르벨로스의 오늘의 점성술을 확인합니다.")
async def astrology(interaction: discord.Interaction):
    result = generate_astrology(interaction.user.id)
    embed = build_embed(result, interaction.user.display_name)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="핑", description="봇 상태를 확인합니다.")
async def ping(interaction: discord.Interaction):
    now_text = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
    await interaction.response.send_message(
        f"퐁! 바르벨로스가 별의 흐름을 관측 중입니다.\n현재 한국 시간: `{now_text} KST`"
    )


bot.run(TOKEN)
