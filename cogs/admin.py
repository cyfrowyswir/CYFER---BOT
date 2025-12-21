import discord
from discord import app_commands
from discord.ext import commands

class Administracja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Komenda BAN z przypisaną permisją
    @app_commands.command(name="ban", description="Banuje użytkownika na serwerze")
    @app_commands.describe(uzytkownik="Kogo chcesz zbanować?", powod="Podaj powód bana")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz zbanować osoby z wyższą lub równą rangą!", ephemeral=True)
        
        await uzytkownik.ban(reason=powod)
        
        emb = discord.Embed(title="🔨 Użytkownik Zbanowany", color=0xff0000)
        emb.add_field(name="Osoba:", value=uzytkownik.mention, inline=True)
        emb.add_field(name="Administrator:", value=interaction.user.mention, inline=True)
        emb.add_field(name="Powód:", value=powod, inline=False)
        
        await interaction.response.send_message(embed=emb)

    # Komenda KICK z przypisaną permisją
    @app_commands.command(name="kick", description="Wyrzuca użytkownika z serwera")
    @app_commands.describe(uzytkownik="Kogo chcesz wyrzucić?", powod="Podaj powód wyrzucenia")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz wyrzucić osoby z wyższą lub równą rangą!", ephemeral=True)
        
        await uzytkownik.kick(reason=powod)
        await interaction.response.send_message(f"✅ Wyrzucono {uzytkownik.mention} za: {powod}")

    # Komenda MUTE (Timeout) z przypisaną permisją
    @app_commands.command(name="mute", description="Nakłada timeout na użytkownika")
    @app_commands.describe(uzytkownik="Komu nałożyć karę?", minuty="Na ile minut?")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int):
        import datetime
        duration = datetime.timedelta(minutes=minuty)
        await uzytkownik.timeout(duration, reason="Kara administracyjna")
        await interaction.response.send_message(f"⏳ Nałożono timeout dla {uzytkownik.mention} na {minuty} minut.")

async def setup(bot):
    await bot.add_cog(Administracja(bot))
