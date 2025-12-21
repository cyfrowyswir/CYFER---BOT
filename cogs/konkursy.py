import discord
from discord import app_commands
from discord.ext import commands

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy prestiżowy panel konkursowy w GUI")
    @app_commands.describe(
        nagroda="Co jest nagrodą główną?",
        koniec="Kiedy kończy się konkurs? (np. za 48h)",
        wymagania="Jakie są zasady wzięcia udziału?"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction, nagroda: str, koniec: str, wymagania: str = "Brak"):
        # Budowanie pięknego Embedu
        emb = discord.Embed(
            title="🎊  WIELKI KONKURS NA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!  🎊",
            description=(
                "### ✨ Weź udział i zgarnij nagrody!\n\n"
                f"🎁 **Nagroda Główna:**\n> `{nagroda}`\n\n"
                f"⏳ **Czas trwania:**\n> `{koniec}`\n\n"
                f"📝 **Wymagania:**\n> {wymagania}\n\n"
                "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                "**Aby dołączyć do losowania, kliknij 🎉 poniżej!**"
            ),
            color=0xf1c40f # Prestiżowy złoty kolor
        )
        
        # Miniaturka serwera w prawym górnym rogu
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
            
        # Stopka z organizatorem i datą
        emb.set_footer(
            text=f"Organizator: {interaction.user.display_name} • Powodzenia!", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        # Najpierw wysyłamy informację zwrotną dla bota
        await interaction.response.send_message("✅ Panel konkursowy został pomyślnie utworzony!", ephemeral=True)
        
        # Wysyłamy właściwy panel na kanał i dodajemy reakcję 🎉
        msg = await interaction.channel.send(embed=emb)
        await msg.add_reaction("🎉")

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
