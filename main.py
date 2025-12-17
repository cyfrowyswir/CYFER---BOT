import discord
import os
from discord.ext import commands

# Podstawowa konfiguracja bota
intents = discord.Intents.default()
intents.message_content = True  # Pozwala czytać treść wiadomości
intents.members = True          # Pozwala widzieć użytkowników

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # Ten napis zobaczysz w logach Koyeb, gdy bot wstanie
    print(f'Bot {bot.user} jest online i gotowy!')

# --- KOMENDA: PING (do sprawdzania czy żyje) ---
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! Opóźnienie: {round(bot.latency * 1000)}ms')

# --- KOMENDA: WYCZYŚĆ (pomaga sprzątać kanał) ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, ilosc: int):
    await ctx.channel.purge(limit=ilosc + 1)
    await ctx.send(f'🗑️ Usunięto {ilosc} wiadomości.', delete_after=3)

# --- KOMENDA: REGULAMIN (Dynamiczny) ---
# Użycie: !regulamin Tytuł | Treść regulaminu
@bot.command()
@commands.has_permissions(administrator=True)
async def regulamin(ctx, *, tekst: str):
    # Sprawdzamy, czy użyłeś kreski | do oddzielenia tytułu
    if "|" in tekst:
        tytul, opis = tekst.split("|", 1)
    else:
        tytul = "Regulamin Serwera"
        opis = tekst

    # Tworzenie profesjonalnej ramki (Embed)
    embed = discord.Embed(
        title=tytul.strip(),
        description=opis.strip(),
        color=discord.Color.from_rgb(43, 88, 155) # Twój niebieski
    )
    
    # Dodajemy stopkę z Twoim logiem (jeśli serwer je ma)
    if ctx.guild.icon:
        embed.set_footer(text=f"Serwer: {ctx.guild.name}", icon_url=ctx.guild.icon.url)
    
    # Bot usuwa Twoją komendę, żeby nie śmiecić
    await ctx.message.delete()
    
    # Bot wysyła gotowy regulamin
    await ctx.send(embed=embed)

# Pobieranie tokenu z ustawień Koyeb
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
