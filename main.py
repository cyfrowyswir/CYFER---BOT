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
@commands.has_permissions(administrator=True) # Tylko admin może to wpisać
async def regulamin(ctx):
    # Tworzymy ramkę (Embed)
    embed = discord.Embed(
        title="📜 REGULAMIN SERWERA",
        description="Dołączając do nas, akceptujesz poniższe zasady:",
        color=discord.Color.blue() # Kolor paska z boku
    )
    
    # Dodajemy punkty regulaminu
    embed.add_field(name="§1.0", value="Zakaz obrażania innych użytkowników.", inline=False)
    embed.add_field(name="§1.1", value="Zakaz reklamowania innych serwerów.", inline=False)
    embed.add_field(name="§1.2", value="Słuchaj poleceń administracji.", inline=False)
    
    # Dodajemy stopkę i obrazek (jeśli chcesz)
    embed.set_footer(text="Administracja Cyfer-Bot", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    # Bot usuwa Twoją wiadomość !regulamin i wysyła ładną ramkę
    await ctx.message.delete()
    await ctx.send(embed=embed)

# --- KOMENDA PING ---
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! Opóźnienie: {round(bot.latency * 1000)}ms')

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
