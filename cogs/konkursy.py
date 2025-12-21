import discord
from discord import app_commands, ui
from discord.ext import commands
import asyncio
import random
import re

# Widok z przyciskiem do zapisu uczestników
class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = []

    @discord.ui.button(label="Dołącz do konkursu!", style=discord.ButtonStyle.blurple, emoji="🎉", custom_id="join_giveaway_v2")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            return await interaction.response.send_message("🛡️ Już bierzesz udział w tym konkursie!", ephemeral=True)
        
        self.participants.append(interaction.user.id)
        await interaction.response.send_message("✅ Zostałeś zapisany! Powodzenia!", ephemeral=True)

# Okienko GUI (Modal) do wpisywania danych
class KonkursModal(ui.Modal, title="Ustawienia Konkursu 🎊"):
    nagroda = ui.TextInput(label="Nagroda", placeholder="Co można wygrać?", min_length=2)
    czas = ui.TextInput(label="Czas trwania", placeholder="np. 10s, 5m, 1h, 1d", min_length=2)
    wymagania = ui.TextInput(label="Wymagania", style=discord.TextStyle.paragraph, placeholder="Co trzeba zrobić?", default="Brak", required=False)

    def parse_time(self, time_str):
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        # POPRAWIONY REGEX: \d+ zamiast \num+
        match = re.match(r"^(\d+)([smhd])$", time_str.lower().strip())
        if not match: 
            return None
        val, unit = match.groups()
        return int(val) * units[unit]

    async def on_submit(self, interaction: discord.Interaction):
        seconds = self.parse_time(self.czas.value)
        if seconds is None:
            # Wyświetla błąd, jeśli format czasu jest zły
            return await interaction.response.send_message("❌ Błędny format czasu! Użyj np. 30s, 5m, 1h.", ephemeral=True)

        embed = discord.Embed(
            title="🎊 NOWY KONKURS NA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃! 🎊",
            description=(
                f"### ✨ Wyjątkowa okazja!\n\n"
                f"🎁 **Nagroda:** `{self.nagroda.value}`\n"
                f"⏳ **Koniec za:** `{self.czas.value}`\n"
                f"📝 **Wymagania:** {self.wymagania.value}\n\n"
                "**Kliknij przycisk poniżej, aby wziąć udział!**"
            ),
            color=0xf1c40f
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"Organizator: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        view = GiveawayView()
        await interaction.response.send_message("✅ Konkurs wystartował!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=view)

        # Oczekiwanie na zakończenie konkursu
        await asyncio.sleep(seconds)

        # Losowanie zwycięzcy
        if not view.participants:
            end_embed = discord.Embed(title="❌ Konkurs zakończony", description=f"Nikt nie wziął udziału w losowaniu `{self.nagroda.value}`.", color=0xe74c3c)
            await msg.edit(embed=end_embed, view=None)
        else:
            winner_id = random.choice(view.participants)
            winner = interaction.guild.get_member(winner_id)
            
            win_embed = discord.Embed(
                title="🎊 KONKURS ZAKOŃCZONY! 🎊",
                description=f"🎁 **Nagroda:** `{self.nagroda.value}`\n🏆 **Zwycięzca:** {winner.mention if winner else 'Nieznany użytkownik'}",
                color=0x2ecc71
            )
            await msg.edit(embed=win_embed, view=None)
            await interaction.channel.send(f"🎉 Gratulacje {winner.mention}! Wygrałeś **{self.nagroda.value}**!")

            # Powiadomienie na PV (DM)
            if winner:
                try:
                    await winner.send(
                        f"🎊 **GRATULACJE!** 🎊\n\n"
                        f"Wygrałeś w konkursie na serwerze **{interaction.guild.name}**!\n"
                        f"🎁 **Nagroda:** `{self.nagroda.value}`\n\n"
                        f"Skontaktuj się z {interaction.user.mention}, aby odebrać nagrodę!"
                    )
                except:
                    pass # Użytkownik może mieć zablokowane DM

class Konkursy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Otwiera okno GUI do stworzenia konkursu")
    @app_commands.checks.has_permissions(administrator=True)
    async def konkurs(self, interaction: discord.Interaction):
        # Wywołanie okna Modal
        await interaction.response.send_modal(KonkursModal())

async def setup(bot):
    await bot.add_cog(Konkursy(bot))
