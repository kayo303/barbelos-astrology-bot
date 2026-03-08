import os
import random
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from data import (
    system_texts,
    element_texts,
    region_texts,
    weapon_texts,
    element_pool,
    weapon_pool,
    region_pool,
    strong_enemies,
    playable_characters,
    challenge_rules,
)

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


def build_astrology_embed(result: dict, user_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=system_texts["title"],
        description=f"별과 원소의 흐름을 따라, 오늘 **{user_name}**에게 닿는 징조를 읽어드립니다.",
        color=discord.Color.from_rgb(88, 72, 156),
    )

    embed.add_field(
        name="✦ 오늘의 별빛",
        value=f"**별의 밝기 {result['brightness']}**\n{score_bar(result['brightness'])}",
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
        text=f"{result['kst_display_date']} · KST 기준 · {system_texts['footer']}"
    )

    return embed


def build_multiplayer_embed(
    user_name: str,
    include_element: bool,
    include_weapon: bool,
    include_region: bool,
):
    picks = []

    if include_element:
        picks.append(("원소", random.choice(element_pool)))
    if include_weapon:
        picks.append(("무기", random.choice(weapon_pool)))
    if include_region:
        picks.append(("지역", random.choice(region_pool)))

    if not picks:
        raise ValueError("최소 한 가지 이상 선택해야 합니다.")

    embed = discord.Embed(
        title="🎲 바르벨로스의 조합 추첨",
        description=f"별의 장난이 **{user_name}**에게 새로운 조건을 내렸습니다.",
        color=discord.Color.from_rgb(122, 102, 196),
    )

    for name, value in picks:
        if name == "원소":
            icon = "🔥"
        elif name == "무기":
            icon = "⚔️"
        else:
            icon = "🗺️"

        embed.add_field(
            name=f"{icon} {name}",
            value=f"**{value}**",
            inline=False,
        )
    return embed


def build_strong_enemy_embed(user_name: str, count: int, selected_enemies: list[str]) -> discord.Embed:
    embed = discord.Embed(
        title="⚔️ 바르벨로스의 강적 추첨",
        description=f"**{user_name}** 앞에 나타난 상대입니다.",
        color=discord.Color.from_rgb(150, 72, 90),
    )

    lines = [f"**{idx}.** {name}" for idx, name in enumerate(selected_enemies, start=1)]

    embed.add_field(
        name=f"⚔️ 등장한 강적 ({count})",
        value="\n".join(lines),
        inline=False,
    )
    embed.set_footer(text="강적 랜덤 추첨")
    return embed


def build_character_embed(user_name: str, count: int, selected_characters: list[str]) -> discord.Embed:
    embed = discord.Embed(
        title="🎭 바르벨로스의 캐릭터 추첨",
        description=f"**{user_name}**에게 내려진 인연의 이름입니다.",
        color=discord.Color.from_rgb(110, 92, 170),
    )

    if count == 1:
        value = f"**{selected_characters[0]}**"
    else:
        value = "\n".join(
            [f"**{idx}.** {name}" for idx, name in enumerate(selected_characters, start=1)]
        )

    embed.add_field(
        name="✦ 추첨 결과",
        value=value,
        inline=False,
    )
    return embed


def build_challenge_embed(user_name: str, character: str, enemy: str, rule: str) -> discord.Embed:
    embed = discord.Embed(
        title="🌙 바르벨로스의 티바트 챌린지",
        description=f"별의 흐름이 **{user_name}**에게 이런 시험을 건넸습니다.",
        color=discord.Color.from_rgb(90, 76, 156),
    )

    embed.add_field(name="🎭 캐릭터", value=f"**{character}**", inline=False)
    embed.add_field(name="⚔️ 강적", value=f"**{enemy}**", inline=False)
    embed.add_field(name="📜 제한 조건", value=f"**{rule}**", inline=False)

    return embed


def parse_number_inputs(raw_text: str) -> list[int]:
    parts = re.split(r"[,\s/]+", raw_text.strip())
    numbers = []

    for part in parts:
        if not part:
            continue
        numbers.append(int(part))

    return numbers


def build_number_lottery_embed(user_name: str, totals: list[int], results: list[int]) -> discord.Embed:
    embed = discord.Embed(
        title="🔢 바르벨로스의 번호 추첨",
        description=f"별이 **{user_name}**에게 아래의 수를 건네주었습니다.",
        color=discord.Color.from_rgb(96, 132, 196),
    )

    lines = []
    for idx, (total, result) in enumerate(zip(totals, results), start=1):
        lines.append(f"**{idx}.** 1 ~ {total} → **{result}**")

    embed.add_field(
        name="✦ 추첨 결과",
        value="\n".join(lines),
        inline=False,
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
    embed = build_astrology_embed(result, interaction.user.display_name)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="조합", description="원소 / 무기 / 지역 조합을 랜덤 추첨합니다.")
@app_commands.describe(
    원소="원소를 추첨할지 선택합니다.",
    무기="무기를 함께 추첨할지 선택합니다.",
    지역="지역을 함께 추첨할지 선택합니다.",
)
async def multiplayer_game(
    interaction: discord.Interaction,
    원소: bool = True,
    무기: bool = False,
    지역: bool = False,
):
    try:
        embed = build_multiplayer_embed(
            user_name=interaction.user.display_name,
            include_element=원소,
            include_weapon=무기,
            include_region=지역,
        )
        await interaction.response.send_message(embed=embed)
    except ValueError:
        await interaction.response.send_message(
            "최소 한 가지는 선택해야 합니다. 예: 원소만 / 원소+무기 / 원소+지역 / 전부",
            ephemeral=True,
        )


@bot.tree.command(name="강적", description="강적을 원하는 수만큼 랜덤 추첨합니다.")
@app_commands.describe(개수="추첨할 강적 수를 입력하세요.")
async def strong_enemy(interaction: discord.Interaction, 개수: app_commands.Range[int, 1, 9]):
    if not strong_enemies:
        await interaction.response.send_message(
            "강적 목록이 비어 있습니다. data.py의 strong_enemies를 먼저 채워 주세요.",
            ephemeral=True,
        )
        return

    if 개수 > len(strong_enemies):
        await interaction.response.send_message(
            f"현재 등록된 강적은 {len(strong_enemies)}개입니다. 그 이하의 수를 입력해 주세요.",
            ephemeral=True,
        )
        return

    selected = random.sample(strong_enemies, k=개수)
    embed = build_strong_enemy_embed(interaction.user.display_name, 개수, selected)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="추첨", description="입력한 전체수 범위 안에서 번호를 랜덤 추첨합니다.")
@app_commands.describe(전체수="예: 100 또는 10 50 100 처럼 여러 개 입력 가능")
async def number_lottery(interaction: discord.Interaction, 전체수: str):
    try:
        totals = parse_number_inputs(전체수)
    except ValueError:
        await interaction.response.send_message(
            "숫자만 입력해 주세요. 예: `100` 또는 `10 50 100`",
            ephemeral=True,
        )
        return

    if not totals:
        await interaction.response.send_message(
            "최소 한 개 이상의 숫자를 입력해 주세요.",
            ephemeral=True,
        )
        return

    if any(n < 1 for n in totals):
        await interaction.response.send_message(
            "전체수는 1 이상의 정수만 입력할 수 있습니다.",
            ephemeral=True,
        )
        return

    if len(totals) > 20:
        await interaction.response.send_message(
            "한 번에 최대 20개까지 입력할 수 있습니다.",
            ephemeral=True,
        )
        return

    results = [random.randint(1, total) for total in totals]
    embed = build_number_lottery_embed(interaction.user.display_name, totals, results)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="캐릭터", description="플레이어블 캐릭터를 랜덤 추첨합니다.")
@app_commands.describe(개수="몇 명을 뽑을지 입력하세요. 기본값은 1입니다.")
async def character(interaction: discord.Interaction, 개수: app_commands.Range[int, 1, 10] = 1):
    if not playable_characters:
        await interaction.response.send_message(
            "캐릭터 목록이 비어 있습니다. data.py의 playable_characters를 먼저 채워 주세요.",
            ephemeral=True,
        )
        return

    if 개수 > len(playable_characters):
        await interaction.response.send_message(
            f"현재 등록된 캐릭터는 {len(playable_characters)}명입니다. 그 이하의 수를 입력해 주세요.",
            ephemeral=True,
        )
        return

    selected = random.sample(playable_characters, k=개수)
    embed = build_character_embed(interaction.user.display_name, 개수, selected)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="챌린지", description="캐릭터, 강적, 제한 조건을 랜덤으로 추첨합니다.")
async def challenge(interaction: discord.Interaction):
    if not playable_characters or not strong_enemies or not challenge_rules:
        await interaction.response.send_message(
            "챌린지에 필요한 데이터가 비어 있습니다. data.py를 확인해 주세요.",
            ephemeral=True,
        )
        return

    selected_character = random.choice(playable_characters)
    selected_enemy = random.choice(strong_enemies)
    selected_rule = random.choice(challenge_rules)

    embed = build_challenge_embed(
        user_name=interaction.user.display_name,
        character=selected_character,
        enemy=selected_enemy,
        rule=selected_rule,
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="핑", description="봇 상태를 확인합니다.")
async def ping(interaction: discord.Interaction):
    now_text = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
    await interaction.response.send_message(
        f"바르벨로스가 별의 흐름을 관측 중입니다.\n현재 한국 시간: `{now_text} KST`"
    )


bot.run(TOKEN)
