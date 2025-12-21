import discord
from discord import app_commands
from discord.ext import commands

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy prestiżowy panel konkursowy")
    @app_commands.describe(
        nagroda="Co jest do wygrania?",
        koniec="Kiedy kończymy? (np. 24h, 3 dni)",
        wymagania="Podaj zasady (np. ranga, weryfikacja)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction, nagroda: str, koniec: str, wymagania: str = "Brak"):
        emb = discord.Embed(
            title="🎊 NOWY KONKURS NA ŚWIRHUB! 🎊",
            description=(
                "**Wielka szansa na wygraną! Dołącz do wspólnej zabawy.**\n\n"
                f"🎁 **NAGRODA:** `{nagroda}`\n"
                f"⏳ **CZAS TRWANIA:** `{koniec}`\n\n"
                f"📝 **WYMAGANIA:**\n> {wymagania}\n\n"
                "**Jak wziąć udział?**\n"
                "Wystarczy kliknąć w reakcję 🎉 poniżej!"
            ),
            color=0xf1c40f
        )
        
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
            
        emb.set_footer(
            text=f"Powodzenia życzy {interaction.user.name}", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        await interaction.response.send_message("✅ Panel konkursowy wysłany!", ephemeral=True)
        msg = await interaction.channel.send(embed=emb)
        await msg.add_reaction("🎉")

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
