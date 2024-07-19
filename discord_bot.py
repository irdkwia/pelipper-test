import discord
from discord.ext import commands
from typing import Optional
import threading

from structure.constants import *
from structure.models import *
from structure.database import *
from structure.dungeon_formatter import *

description = '''A bot that notifies users about WFC events in PMD: Explorers of Sky, such as dungeon rescues.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

async def send_signup_code(username_or_id: str, signup_code: str):
    user = await get_user_by_username_or_id(username_or_id)
    if user:
        await user.send("Welcome to the Pelipper notification service!\n\nYour sign-up code is: " + signup_code)
    else:
        raise Exception("Failed to find user: " + username_or_id)

async def notify_rescue(username_or_id: Optional[str], team: str, title: str, message: str, dungeon_info: str, code: str):
    if not DISCORD_UPDATE_CHANNEL_ID:
        return

    channel = bot.get_channel(DISCORD_UPDATE_CHANNEL_ID)

    user = None
    if username_or_id:
        user = await get_user_by_username_or_id(username_or_id)

    description = f"Team {team} requested a rescue!"
    if user:
        description = f"<@{user.id}> requested a rescue!"

    embed = discord.Embed(title=f"New SOS Mail", description=description, color=0xff0000)
    embed.add_field(name="Team Name", value=team, inline=False)
    embed.add_field(name="Dungeon", value=dungeon_info, inline=False)
    embed.add_field(name="Rescue Number", value=code, inline=False)
    if title:
        embed.add_field(name="Title", value=title, inline=False)
    if message:
        embed.add_field(name="Message", value=message, inline=False)
    try:
        await channel.send(embed=embed)
    except Exception as error:
        print("Error:", error)

async def send_aok(rescued_username_or_id: Optional[str], rescuer_username_or_id: Optional[str], rescued_team: str, rescuer_team: str, title: str, message: str, dungeon_info: str, code: str):
    def apply_embed_fields(embed: discord.Embed):
        embed.add_field(name="Rescued Team", value=rescued_team)
        embed.add_field(name="Rescuer", value=rescuer_team)
        embed.add_field(name="Dungeon", value=dungeon_info)
        embed.add_field(name="Rescue Number", value=code)
        if title:
            embed.add_field(name="Title", value=title, inline=False)
        if message:
            embed.add_field(name="Message", value=message, inline=False)

    rescued_user = await get_user_by_username_or_id(rescued_username_or_id)
    rescuer_user = await get_user_by_username_or_id(rescuer_username_or_id)

    if DISCORD_UPDATE_CHANNEL_ID:
        channel = bot.get_channel(DISCORD_UPDATE_CHANNEL_ID)

        description_rescuer = f"Team {rescuer_team}"
        if rescuer_user:
            description_rescuer = f"<@{rescuer_user.id}>"
        description_rescued = f"Team {rescued_team}"
        if rescued_user:
            description_rescued = f"<@{rescued_user.id}>"
        description = f"{description_rescuer} has rescued {description_rescued}!"
        embed = discord.Embed(title="New A-OK Mail", description=description, color=0x00ff00)

        apply_embed_fields(embed)
        await channel.send(embed=embed)
        
    if rescued_user:
        description = f"You've received an A-OK Mail from Team {rescuer_team}!"
        if rescuer_user:
            description = f"You've received an A-OK Mail from <@{rescuer_user.id}>!"
        embed = discord.Embed(title="New A-OK Mail", description=description, color=0x00ff00)
        apply_embed_fields(embed)
        await rescued_user.send(embed=embed)
    else:
        raise Exception("Failed to find user: " + rescued_username_or_id)
    
async def send_thank_you(username_or_id: str, title: str, message: str):
    user = await get_user_by_username_or_id(username_or_id)

    if user:
        embed = discord.Embed(title="New Thank-You Mail", description="You've received a Thank-You Mail!", color=0x0000ff)
        if title:
            embed.add_field(name="Title", value=title, inline=False)
        if message:
            embed.add_field(name="Message", value=message, inline=False)
        await user.send(embed=embed)
    else:
        raise Exception("Failed to find user: " + username_or_id)

async def get_user_by_username_or_id(username_or_id: str) -> Optional[discord.User]:
    """Retrieve a user by user name or ID. The user has to share a guild with the bot."""
    try:
        user = await bot.fetch_user(username_or_id)
        if user:
            return user
    except:
        pass

    for guild in bot.guilds:
        def pred(m: discord.Member) -> bool:
            return m.name == username_or_id

        user = discord.utils.find(pred, guild.members)
        if user:
            return user
        
    return None

event_loop = None

def run():
    bot.run(DISCORD_TOKEN)

bot = None
enabled = False

if DISCORD_TOKEN:
    bot = commands.Bot(command_prefix='?', description=description, intents=intents)

    bot_thread = threading.Thread(target=run)
    bot_thread.start()

    enabled = True
