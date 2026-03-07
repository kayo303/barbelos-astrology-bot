import os
import random
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from data import system_texts, element_texts, region_texts, weapon_texts

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN 이 설정되지 않았습니다.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def pick_random_entry(rng: random.Random, data_dict: dict):
    name = rng.choice(list(data_dict.keys()))
    text = rng.choice(data_dict[name])
    return name, text


def score_bar(score: int) -> str:
    filled = max(1, score // 10)
    empty = 10 - filled
    return "★" * filled + "☆" * empty + f" ({score})"


def generate_astrology(user_id: int):
    today = datetime.date.today().isoformat()
    rng = random.Random(f"{user_id}-{today}")

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

    overall = (f"오늘의 별은 **{element_name}**의 흐름과 **{region_name}**의 기운, "
               f"그리고 **{weapon_name}**의 징조를 함께 비추고 있습니다.\n"
               f"별의 기록은 오늘 하루 같은 방향을 가리키니, 조급해하지 말고 흐름을 읽으세요.")

    return {
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

    embed = discord.Embed(
        title=system_texts["title"],
        description=system_texts["description"],
        color=discord.Color.purple(),
    )

    embed.add_field(
        name="오늘의 원소",
        value=f"**{result['element_name']}**\n{result['element_text']}",
        inline=False,
    )
    embed.add_field(
        name="오늘의 지역",
        value=f"**{result['region_name']}**\n{result['region_text']}",
        inline=False,
    )
    embed.add_field(
        name="오늘의 무기",
        value=f"**{result['weapon_name']}**\n{result['weapon_text']}",
        inline=False,
    )
    embed.add_field(
        name="종합 점성 결과",
        value=result["overall"],
        inline=False,
    )

    embed.add_field(name="학업의 흐름",
                    value=score_bar(result["study_score"]),
                    inline=False)
    embed.add_field(name="관계의 흐름",
                    value=score_bar(result["relationship_score"]),
                    inline=False)
    embed.add_field(name="영혼의 흐름",
                    value=score_bar(result["soul_score"]),
                    inline=False)
    embed.add_field(name="재물의 흐름",
                    value=score_bar(result["wealth_score"]),
                    inline=False)
    embed.add_field(name="신체의 흐름",
                    value=score_bar(result["body_score"]),
                    inline=False)
    embed.add_field(name="기원의 흐름",
                    value=score_bar(result["wish_score"]),
                    inline=False)

    embed.set_footer(
        text=
        f"{system_texts['brightness_label']} {result['brightness']} · {system_texts['footer']}"
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="핑", description="봇 상태를 확인합니다.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("퐁! 바르벨로스가 별의 흐름을 관측 중입니다.")


bot.run(TOKEN)
