import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime

# --- MODAL: KREATOR KONKURSU ---
class GiveawayModal(discord.ui.Modal, title="Kreator Konkursu 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    nagroda = discord.ui.TextInput(label="Nagroda", placeholder="Np. Ranga VIP", required=True)
    czas = discord.ui.TextInput(label="Czas trwania (minuty)", placeholder="Np. 60", required=True)
    wygrani = discord.ui.TextInput(label="Liczba zwycięzców", default="1", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(self.czas.value)
            winners_count = int(self.wygrani.value)
        except ValueError:
            return await interaction.response.send_message("❌ Czas i liczba zwycięzców muszą być liczbami!", ephemeral=True)

        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        timestamp = f"<t:{int(end_time.timestamp())}:R>"

        embed = discord.Embed(
            title="🎉 TRWA KONKURS! 🎉",
            description=(
                f"**𝑺 𝑾 𝑰 𝑹 𝑯 𝑼 𝑩**\n\n"
                f"🎁 Nagroda: **{self.nagroda.value}**\n"
                f"⌛ Koniec: {timestamp}\n"
                f"👥 Wygrani: **{winners_count}**\n\n"
                "Kliknij przycisk poniżej, aby dołączyć!"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Konkursy • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # Link do banneru KONKURS (możesz podmienić)
        embed.set_image(url="https://twoj-link.pl/konkurs_start.png")

        view = GiveawayView(self.nagroda.value, end_time, winners_count)
        await interaction.response.send_message("✅ Konkurs wystartował!", ephemeral=True)
        message = await interaction.channel.send(embed=embed, view=view)
        
        await asyncio.sleep(minutes * 60)
        await view.end_giveaway(message)

# --- VIEW: OBSŁUGA KONKURSU ---
class GiveawayView(discord.ui.View):
    def __init__(self, prize, end_time, winners_count):
        super().__init__(timeout=None)
        self.prize = prize
        self.end_time = end_time
        self.winners_count = winners_count
        self.participants = []

    @discord.ui.button(label="Dołącz do konkursu", style=discord.ButtonStyle.success, emoji="🎉", custom_id="join_give")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            return await interaction.response.send_message("Już bierzesz udział!", ephemeral=True)
        
        self.participants.append(interaction.user.id)
        await interaction.response.send_message("✅ Zapisano Cię do konkursu!", ephemeral=True)

    async def end_giveaway(self, message: discord.Message):
        self.stop()
        
        # Generowanie widoku zakończenia (jak na Twoim screenie)
        if not self.participants:
            winner_text = "Brak uczestników."
            winners_mention = "Nikt"
        else:
            winners = random.sample(self.participants, min(len(self.participants), self.winners_count))
            winners_mention = ", ".join([f"<@{w_id}>" for w_id in winners])
            winner_text = winners_mention

        end_embed = discord.Embed(
            title="🎉 Konkurs zakończony!",
            description=(
                f"**Co było do wygrania:** {self.prize}\n"
                f"**Ilość osób, które dołączyły:** {len(self.participants)}\n"
                f"**Status:** Konkurs zakończony!\n\n"
                f"👑 **Zwycięzcy konkursu:** 👑\n"
                f"{winner_text}"
            ),
            color=discord.Color.red() # Czerwony pasek jak na screenie
        )
        
        # Miniaturka serwera w rogu
        if message.guild.icon:
            end_embed.set_thumbnail(url=message.guild.icon.url)
        
        # Banner KONKURS ZAKOŃCZONY ze screena
        end_embed.set_image(url="https://twoj-link.pl/konkurs_zakonczony.png")
        
        # Data zakończenia w stopce
        current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        end_embed.set_footer(text=f"{current_time} • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")

        # Przycisk staje się nieaktywny
        disabled_view = discord.ui.View()
        disabled_view.add_item(discord.ui.Button(label="Konkurs zakończony", style=discord.ButtonStyle.danger, disabled=True))

        await message.edit(embed=end_embed, view=disabled_view)
        if self.participants:
            await message.channel.send(f"🎊 Gratulacje {winners_mention}! Wygrałeś/aś: **{self.prize}**!")

# --- COG ---
class Konkursy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="konkurs", description="Tworzy nowy konkurs 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def konkurs(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GiveawayModal())

async def setup(bot: commands.Bot):
    await bot.add_cog(Konkursy(bot))
