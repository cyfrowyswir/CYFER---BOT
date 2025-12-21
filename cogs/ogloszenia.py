import discord
from discord import app_commands
from discord.ext import commands

class Ogloszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tekst", description="Tworzy profesjonalne ogłoszenie w pełnej ramce")
    @app_commands.describe(
        tytul="Podaj tytuł ogłoszenia",
        tresc="Wpisz treść (możesz używać \n dla nowej linii)",
        kolor="Wybierz: niebieski, zielony, czerwony, zloty"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def tekst(self, interaction: discord.Interaction, tytul: str, tresc: str, kolor: str = "niebieski"):
        kolory = {"niebieski": 0x5865F2, "zielony": 0x2ecc71, "czerwony": 0xe74c3c, "zloty": 0xf1c40f}
        wybrany_kolor = kolory.get(kolor.lower(), 0x5865F2)

        emb = discord.Embed(
            title=f"📢 {tytul}",
            description=f"\n{tresc.replace('\\n', '\n')}\n", # Dodatkowe światło w tekście
            color=wybrany_kolor
        )
        
        # Przywrócenie bogatego wyglądu
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        emb.set_footer(
            text=f"Oficjalne ogłoszenie • {interaction.user.name}", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie opublikowane!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ogloszenia(bot))
