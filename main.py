import discord
import os
from discord.ext import commands

# 1. Konfiguracja uprawnień (BARDZO WAŻNE)
intents = discord.Intents.default()
intents.message_content = True  # Musi być włączone, żeby bot czytał komendy
intents.members = True

# 2. Tworzenie bota z prefixem "!" (np. !regulamin)
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ZDARZENIE: START BOTA ---
@bot.event
async def on_ready():
    print(f'✅ SUKCES: Bot {bot.user} jest zalogowany i gotowy!')
    # Ustawia status bota na "Ogląda: Wasz Serwer"
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Wasz Serwer"))

# --- KOMENDA: PING (Testowa) ---
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! ({round(bot.latency * 1000)}ms)')

# --- KOMENDA: REGULAMIN (Główna) ---
@bot.command()
@commands.has_permissions(administrator=True) # Tylko admin może użyć
async def regulamin(ctx, *, tresc: str = None):
    # Jeśli ktoś wpisze samo !regulamin bez tekstu
    if tresc is None:
        await ctx.send("❌ Błąd: Musisz wpisać treść! Użyj: `!regulamin Tytuł | Treść`")
        return

    # Dzielimy tekst na Tytuł i Opis znakiem "|"
    if "|" in tresc:
        tytul, opis = tresc.split("|", 1)
    else:
        # Jeśli nie dasz kreski, całość będzie opisem
        tytul = "📢 OGŁOSZENIE"
        opis = tresc

    # Tworzenie ładnej ramki (Embed)
    embed = discord.Embed(
        title=tytul.strip(),
        description=opis.strip().replace("\\n", "\n"), # Zamienia \n na nową linię
        color=0x2b589b # Twój niebieski kolor
    )

    # Dodanie stopki z logiem serwera (jeśli jest)
    if ctx.guild.icon:
        embed.set_footer(text=f"Administracja {ctx.guild.name}", icon_url=ctx.guild.icon.url)
    else:
        embed.set_footer(text=f"Administracja {ctx.guild.name}")

    # Usuwanie Twojej wiadomości z komendą i wysłanie ramki
    await ctx.message.delete()
    await ctx.send(embed=embed)

# --- URUCHAMIANIE ---
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ BŁĄD: Nie znaleziono tokena w zmiennych środowiskowych!")
