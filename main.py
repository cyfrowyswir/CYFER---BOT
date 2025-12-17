import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} online!')

@bot.command()
async def hej(ctx):
    await ctx.send('Cześć! Twój bot działa i ma się świetnie.')

# Pobiera token z ustawień Koyeb
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
