import discord
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio

class Administracja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def wyslij_pv(self, uzytkownik, tytul, powod, kolor, gildia, admin):
        emb = discord.Embed(
            title=tytul,
            description=f"**Serwer:** {gildia}\n**Powód:** {powod}\n**Administrator:** {admin}",
            color=kolor
        )
        emb.timestamp = discord.utils.utcnow()
        try:
            await uzytkownik.send(embed=emb)
        except:
            pass

    @app_commands.command(name="tempban", description="Banuje użytkownika na określony czas")
    @app_commands.describe(
        uzytkownik="Kogo chcesz zbanować?", 
        czas="Liczba (np. 10)", 
        jednostka="Wybierz: Minuty, Godziny, Dni",
        powod="Podaj powód bana"
    )
    @app_commands.choices(jednostka=[
        app_commands.Choice(name="Minuty", value="m"),
        app_commands.Choice(name="Godziny", value="h"),
        app_commands.Choice(name="Dni", value="d")
    ])
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction, uzytkownik: discord.Member, czas: int, jednostka: app_commands.Choice[str], powod: str = "Brak powodu"):
        if uzytkownik.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Nie możesz zbanować tej osoby!", ephemeral=True)

        # Przeliczanie czasu na sekundy
        sekundy = 0
        czas_tekst = ""
        if jednostka.value == "m":
            sekundy = czas * 60
            czas_tekst = f"{czas} min"
        elif jednostka.value == "h":
            sekundy = czas * 3600
            czas_tekst = f"{czas} godz"
        elif jednostka.value == "d":
            sekundy = czas * 86400
            czas_tekst = f"{czas} dni"

        # Wysyłanie PW
        await self.wyslij_pv(
            uzytkownik, 
            f"⏳ Zostałeś ZBANOWANY CZASOWO na {interaction.guild.name}", 
            f"{powod} (Czas: {czas_tekst})", 
            0xffa500, 
            interaction.guild.name, 
            interaction.user.name
        )

        await uzytkownik.ban(reason=f"Tempban: {powod} ({czas_tekst})")
        await interaction.response.send_message(f"✅ Zbanowano {uzytkownik.mention} na **{czas_tekst}**.", ephemeral=True)

        # Czekanie i Unban
        await asyncio.sleep(sekundy)
        try:
            await interaction.guild.unban(uzytkownik, reason="Koniec czasu bana")
        except:
            pass # Jeśli został odbanowany ręcznie wcześniej

    # Reszta Twoich komend (kick, ban, mute) zostaje bez zmian pod spodem...
