import discord
from discord import app_commands
from discord.ext import commands

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy prestiżowy panel konkursowy")
    @app_commands.describe(
        nagroda="Co można wygrać?",
        koniec="Czas trwania (np. 24h)",
        wymagania="Co trzeba zrobić, żeby wygrać?"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction, nagroda: str, koniec: str, wymagania: str = "Brak wymagań"):
        # Bogaty design embeda
        emb = discord.Embed(
            title="🎉  WIELKI KONKURS  🎉",
            description=(
                "**Zapraszamy wszystkich do udziału!**\n\n"
                f"🎁 **NAGRODA GŁÓWNA:**\n> `{nagroda}`\n\n"
                f"⏳ **KONIEC ZA:**\n> `{koniec}`\n\n"
                f"📝 **WYMAGANIA:**\n> {wymagania}\n\n"
                "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                "**Aby wziąć udział, zostaw reakcję 🎉 pod tą wiadomością!**"
            ),
            color=0xf1c40f # Złoty kolor
        )
        
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
            
        emb.set_footer(
            text=f"Organizator: {interaction.user.display_name} • Powodzenia!", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        # Najpierw odpowiadamy na interakcję (żeby nie było błędu "nie reaguje")
        await interaction.response.send_message("✅ Konkurs został utworzony!", ephemeral=True)
        
        # Potem wysyłamy embed i dajemy reakcję
        msg = await interaction.channel.send(embed=emb)
        await msg.add_reaction("🎉")

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
