import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Pozwala botowi widzieć użytkowników

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} online i gotowy do pracy!')

# --- KOMENDA NA REGULAMIN ---
@bot.command()
@commands.has_permissions(administrator=True)
async def regulamin(ctx, *, wiadomosc: str):
    # Dzielimy wiadomość na tytuł i opis używając znaku "|"
    if "|" in wiadomosc:
        tytul, opis = wiadomosc.split("|", 1)
    else:
        tytul = "Regulamin Serwera"
        opis = wiadomosc

    embed = discord.Embed(
        title=tytul.strip(),
        description=opis.strip(),
        color=discord.Color.blue()
    )
    
    embed.set_footer(text=f"Wysłane przez: {ctx.author.name}")
    
    await ctx.message.delete() # Usuwa Twoją komendę, zostaje tylko embed
    await ctx.send(embed=embed)

# --- KOMENDA PING ---
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! Opóźnienie: {round(bot.latency * 1000)}ms')

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
