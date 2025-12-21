import discord
from discord import app_commands
from discord.ext import commands
import datetime

class Administracja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def wyslij_pv(self, uzytkownik, tytul, powod, kolor, gildia, admin):
        """Pomocnicza funkcja do wysyłania PW"""
        emb = discord.Embed(
            title=tytul,
            description=f"**Serwer:** {gildia}\n**Powód:** {powod}\n**Administrator:** {admin}",
            color=kolor
        )
        emb.timestamp = discord.utils.utcnow()
        try:
            await uzytkownik.send(embed=emb)
            return True
        except:
            return False

    @app_commands.command(name="kick", description="Wyrzuca gracza i wysyła mu info na PW")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz wyrzucić tej osoby!", ephemeral=True)
        
        # Wysyłamy PW przed kickiem
        await self.wyslij_pv(uzytkownik, f"🚪 Zostałeś wyrzucony z {interaction.guild.name}", powod, 0xe74c3c, interaction.guild.name, interaction.user.name)
        
        await uzytkownik.kick(reason=powod)
        await interaction.response.send_message(f"✅ Wyrzucono {uzytkownik.mention}.", ephemeral=True)

    @app_commands.command(name="ban", description="Banuje gracza i wysyła mu info na PW")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz zbanować tej osoby!", ephemeral=True)

        # Wysyłamy PW przed banem
        await self.wyslij_pv(uzytkownik, f"🔨 Zostałeś ZBANOWANY na {interaction.guild.name}", powod, 0xff0000, interaction.guild.name, interaction.user.name)
        
        await uzytkownik.ban(reason=powod)
        await interaction.response.send_message(f"✅ Zbanowano {uzytkownik.mention}.", ephemeral=True)

    @app_commands.command(name="mute", description="Nakłada timeout i wysyła info na PW")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int, powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz wyciszyć tej osoby!", ephemeral=True)

        duration = datetime.timedelta(minutes=minuty)
        
        # Wysyłamy PW przed nałożeniem kary
        await self.wyslij_pv(uzytkownik, f"⏳ Zostałeś wyciszony na {interaction.guild.name}", f"{powod} (Czas: {minuty} min)", 0xf1c40f, interaction.guild.name, interaction.user.name)
        
        await uzytkownik.timeout(duration, reason=powod)
        await interaction.response.send_message(f"✅ Wyciszono {uzytkownik.mention} na {minuty} minut.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Administracja(bot))
