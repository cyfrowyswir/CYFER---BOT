import discord
from discord import app_commands
from discord.ext import commands

class Ogloszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tekst", description="Tworzy profesjonalne ogłoszenie w pełnej ramce")
    @app_commands.describe(
        tytul="Nagłówek ogłoszenia",
        tresc="Treść (użyj \\n aby zrobić nową linię)",
        kolor="Wybierz kolor ramki"
    )
    @app_commands.choices(kolor=[
        app_commands.Choice(name="Niebieski (Info)", value="niebieski"),
        app_commands.Choice(name="Zielony (Sukces)", value="zielony"),
        app_commands.Choice(name="Czerwony (Alarm)", value="czerwony"),
        app_commands.Choice(name="Złoty (Specjalny)", value="zloty")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def tekst(self, interaction: discord.Interaction, tytul: str, tresc: str, kolor: app_commands.Choice[str]):
        # Mapa kolorów
        kolory_hex = {
            "niebieski": 0x5865F2,
            "zielony": 0x2ecc71,
            "czerwony": 0xe74c3c,
            "zloty": 0xf1c40f
        }
        wybrany_kolor = kolory_hex.get(kolor.value, 0x5865F2)

        # Tworzenie "pięknego" embeda
        emb = discord.Embed(
            title=f"📢  {tytul}",
            description=f"\n{tresc.replace('\\n', '\n')}\n", # Obsługa nowych linii
            color=wybrany_kolor
        )
        
        # Miniaturka serwera w rogu
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        # Stopka z autorem
        emb.set_footer(
            text=f"Ogłoszenie od: {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Wysłano ogłoszenie!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ogloszenia(bot))
