import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Usuwa określoną liczbę wiadomości")
    @app_commands.describe(ilosc="Liczba wiadomości do usunięcia")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        if ilosc < 1 or ilosc > 100:
            return await interaction.response.send_message("❌ Możesz usunąć od 1 do 100 wiadomości na raz.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=ilosc)

        embed = discord.Embed(
            title="🧹 Czystka wykonana!",
            description=(
                f"**𝑺 𝑾 𝑰 Ｒ Ｈ 𝑼 𝑩**\n\n"
                f"👤 Moderator: {interaction.user.mention}\n"
                f"💬 Usunięto: **{len(deleted)}** wiadomości\n"
                f"📂 Kanał: {interaction.channel.mention}"
            ),
            color=discord.Color.from_rgb(255, 0, 255)
        )
        embed.set_footer(text="Administracja • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        embed.set_timestamp()

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ban", description="Banuje użytkownika na serwerze")
    @app_commands.describe(uzytkownik="Kogo chcesz zbanować?", powod="Powód bana")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz zbanować osoby z wyższą lub równą rolą!", ephemeral=True)

        try:
            await uzytkownik.ban(reason=powod)
            embed = discord.Embed(
                title="🔨 Użytkownik Zbanowany",
                description=(
                    f"**𝑺 𝑾 𝑰 Ｒ Ｈ 𝑼 𝑩**\n\n"
                    f"👤 Zbanowany: **{uzytkownik.name}**\n"
                    f"👮 Moderator: {interaction.user.mention}\n"
                    f"📝 Powód: `{powod}`"
                ),
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=uzytkownik.display_avatar.url)
            embed.set_footer(text="System Kar • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Wyrzuca użytkownika z serwera")
    @app_commands.describe(uzytkownik="Kogo chcesz wyrzucić?", powod="Powód wyrzucenia")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz wyrzucić tej osoby!", ephemeral=True)

        try:
            await uzytkownik.kick(reason=powod)
            embed = discord.Embed(
                title="👢 Użytkownik Wyrzucony",
                description=(
                    f"**𝑺 𝑾 𝑰 Ｒ Ｈ 𝑼 𝑩**\n\n"
                    f"👤 Wyrzucony: **{uzytkownik.name}**\n"
                    f"👮 Moderator: {interaction.user.mention}\n"
                    f"📝 Powód: `{powod}`"
                ),
                color=discord.Color.orange()
            )
            embed.set_footer(text="System Kar • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

    @app_commands.command(name="say", description="Wysyła wiadomość jako bot (zwykły tekst)")
    @app_commands.checks.has_permissions(administrator=True)
    async def say(self, interaction: discord.Interaction, tresc: str):
        await interaction.channel.send(tresc)
        await interaction.response.send_message("✅ Wysłano.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
