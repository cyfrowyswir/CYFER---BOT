import discord
from discord import app_commands
from discord.ext import commands

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy estetyczny panel konkursowy")
    @app_commands.describe(
        nagroda="Co można wygrać?",
        koniec="Czas trwania (np. 24h)",
        wymagania="Co trzeba zrobić?"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction, nagroda: str, koniec: str, wymagania: str = "Brak"):
        emb = discord.Embed(
            title="🎊 NOWY KONKURS! 🎊",
            description=(
                f"🎁 **Nagroda:** `{nagroda}`\n"
                f"⏳ **Koniec:** `{koniec}`\n"
                f"📝 **Wymagania:** {wymagania}\n\n"
                "Kliknij reakcję 🎉 poniżej, aby dołączyć!"
            ),
            color=0xf1c40f
        )
        
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        emb.set_footer(text=f"Organizator: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        # Wysyłanie
        await interaction.response.send_message("✅ Konkurs wystartował!", ephemeral=True)
        msg = await interaction.channel.send(embed=emb)
        await msg.add_reaction("🎉")

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
