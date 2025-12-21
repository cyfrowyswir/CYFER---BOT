import discord
from discord import app_commands
from discord.ext import commands
import datetime

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy profesjonalny panel konkursowy")
    @app_commands.describe(
        nagroda="Co jest do wygrania?",
        koniec="Kiedy kończy się konkurs? (np. za 24h, za 3 dni)",
        wymagania="Jakie są wymagania? (np. brak)",
        ilosc_zwyciezcow="Ilu graczy wygrywa?"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction, nagroda: str, koniec: str, wymagania: str = "Brak", ilosc_zwyciezcow: int = 1):
        # Tworzenie estetycznego Embedu
        emb = discord.Embed(
            title="🎊 NOWY KONKURS! 🎊",
            description=(
                f"Szykujcie się! Mamy dla Was coś specjalnego.\n\n"
                f"🎁 **Nagroda:** `{nagroda}`\n"
                f"👥 **Ilość zwycięzców:** `{ilosc_zwyciezcow}`\n"
                f"⏳ **Koniec za:** `{koniec}`\n\n"
                f"📝 **Wymagania:**\n{wymagania}\n\n"
                f"Aby wziąć udział, kliknij w reakcję 🎉 poniżej!"
            ),
            color=0xf1c40f # Złoty kolor konkursowy
        )
        
        # Dodajemy grafikę konkursową w rogu
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
            
        # Dodajemy duży obrazek (możesz tu wkleić swój link do grafiki)
        emb.set_image(url="https://i.imgur.com/uVf3KUn.png")
        
        emb.set_footer(
            text=f"Organizator: {interaction.user.name} • Powodzenia!", 
            icon_url=interaction.user.display_avatar.url
        )
        
        # Wysyłanie i dodanie reakcji
        await interaction.response.send_message("✅ Konkurs został opublikowany!", ephemeral=True)
        msg = await interaction.channel.send(embed=emb)
        await msg.add_reaction("🎉")

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
