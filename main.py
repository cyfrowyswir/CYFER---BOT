import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

    async def update_status(self):
        total_members = sum(guild.member_count for guild in self.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"monitoruje {total_members} osób"
        )
        await self.change_presence(activity=activity)

bot = SwirHubBot()

# --- MODAL KONKURSU ---
def parse_duration(duration_str):
    time_dict = {"s": 1, "m": 60, "h": 3600}
    match = re.match(r"(\d+)([smh])", duration_str.lower())
    if match:
        amount, unit = match.groups()
        return int(amount) * time_dict[unit]
    return None

class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Dołącz 🎉", style=discord.ButtonStyle.blurple, custom_id="join_giveaway")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("❌ Już bierzesz udział!", ephemeral=True)
        self.participants.append(interaction.user)
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Uczestników: {len(self.participants)} | Powodzenia!")
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ Dołączyłeś!", ephemeral=True)

class KonkursModal(Modal, title="Uruchom Konkurs 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    nagroda = TextInput(label="Nagroda", required=True)
    czas = TextInput(label="Czas (np. 30s, 10m, 2h)", required=True)
    opis = TextInput(label="Zasady", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_duration(self.czas.value)
        if not seconds:
            return await interaction.response.send_message("❌ Zły format czasu!", ephemeral=True)
        view = GiveawayView(timeout=seconds)
        emb = discord.Embed(title="🎉 NOWY KONKURS 🎉", description=f"**Nagroda:** {self.nagroda.value}\n**Czas:** {self.czas.value}\n{self.opis.value if self.opis.value else ''}", color=0xF1C40F)
        await interaction.response.send_message("✅ Wystartowano!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        await asyncio.sleep(seconds)
        if len(view.participants) > 0:
            winner = random.choice(view.participants)
            await interaction.channel.send(f"🎊 Konkurs zakończony! Wygrywa: {winner.mention} (**{self.nagroda.value}**)")
        else:
            await interaction.channel.send(f"❌ Brak uczestników w konkursie na {self.nagroda.value}.")
        await msg.edit(view=None)

# --- SYSTEM POWITAŃ I STATUSU ---
@bot.event
async def on_member_join(member):
    await bot.update_status() # Aktualizacja licznika osób w profilu
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="👋 Witamy w 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!", description=f"Siema {member.mention}!", color=THEME_COLOR)
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member):
    await bot.update_status() # Aktualizacja licznika osób w profilu

# --- SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Usuwanie za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz kategorię...", custom_id="t_select", options=[
        discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
        discord.SelectOption(label="Zamówienie-MC", emoji="⛏️"),
        discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨")
    ])
    async def callback(self, interaction, select):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=discord.Embed(title=f"Ticket: {select.values[0]}", color=THEME_COLOR), view=TicketControlView())
        await interaction.response.send_message(f"✅ {ch.mention}", ephemeral=True)

# --- WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="konkurs")
async def konkurs_cmd(interaction): await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="weryfikacja")
async def v_cmd(interaction):
    await interaction.channel.send(embed=discord.Embed(title="Weryfikacja 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", description="Kliknij przycisk!", color=THEME_COLOR), view=VerifyView())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="ticket")
async def t_cmd(interaction):
    await interaction.channel.send(embed=discord.Embed(title="Tickety 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", description="Otwórz zgłoszenie.", color=THEME_COLOR), view=TicketLauncher())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="clear")
async def clear_cmd(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"✅ Usunięto {ilosc} wiadomości.", ephemeral=True)

@bot.command()
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend.")

@bot.event
async def on_ready():
    await bot.update_status() # Ustawia "monitoruje X osób" przy starcie
    print(f"✅ Bot online jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
