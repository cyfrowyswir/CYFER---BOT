import discord
from discord import app_commands
from discord.ext import commands

class Ogloszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tekst", description="Tworzy profesjonalne ogłoszenie w ramce (Embed)")
    @app_commands.describe(
        tytul="Podaj tytuł ogłoszenia (nagłówek)",
        tresc="Wpisz treść ogłoszenia (możesz używać \n dla nowej linii)",
        kolor="Wybierz kolor (niebieski, zielony, czerwony, złoty)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def tekst(self, interaction: discord.Interaction, tytul: str, tresc: str, kolor: str = "niebieski"):
        # Mapa kolorów
        kolory = {
            "niebieski": 0x5865F2,
            "zielony": 0x2ecc71,
            "czerwony": 0xe74c3c,
            "zloty": 0xf1c40f
        }
        wybrany_kolor = kolory.get(kolor.lower(), 0x5865F2)

        # Budowanie estetycznego Embedu
        emb = discord.Embed(
            title=f"📢 {tytul}",
            description=tresc.replace("\\n", "\n"), # Pozwala na robienie nowej linii przez wpisanie \n
            color=wybrany_kolor
        )
        
        # Dodajemy ikonę serwera, jeśli istnieje
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        # Stopka z autorem i datą
        emb.set_footer(
            text=f"Wysłano przez: {interaction.user.name} • SwirHub", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie wysłane!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ogloszenia(bot))
