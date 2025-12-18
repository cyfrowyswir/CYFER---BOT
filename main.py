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
        # To sprawia, że przyciski działają nawet po restarcie bota
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

bot = SwirHubBot()

# --- SYSTEM KONKURSU Z PRZYCISKIEM ---

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
        await interaction.response.send_message("✅ Dołączyłeś do konkursu!", ephemeral=True)

class KonkursModal(Modal, title="Uruchom Konkurs 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    nagroda = TextInput(label="Nagroda", placeholder="Co wygrywamy?", required=True)
    czas = TextInput(label="Czas (np. 30s, 10m, 2h)", placeholder="Np. 10m", required=True)
    opis = TextInput(label="Dodatkowe info", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_duration(self.czas.value)
        if not seconds:
            return await interaction.response.send_message("❌ Zły format czasu!", ephemeral=True)

        view = GiveawayView(timeout=seconds)
        emb = discord.Embed(
            title="🎉 NOWY KONKURS 🎉",
            description=f"**Nagroda:** {self.nagroda.value}\n**Czas:** {self.czas.value}\n{self.opis.value if self.opis.value else ''}",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        emb.set_footer(text="Uczestników: 0")
        
        await interaction.response.send_message("✅ Wystartowano!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)

        await asyncio.sleep(seconds)
        
        if len(view.participants) > 0:
            winner = random.choice(view.participants)
            await interaction.channel.send(f"🎊 Konkurs zakończony! Wygrywa: {winner.mention} (**{self.nagroda.value}**)")
        else:
            await interaction.channel.send(f"❌ Nikt nie dołączył do konkursu na **{self.nagroda.value}**.")
        await msg.edit(view=None)

# --- TICKET SYSTEM ---

class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Zamykanie za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(
        placeholder="Wybierz kategorię zgłoszenia...",
        custom_id="ticket_select_menu",
        options=[
            discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
            discord.SelectOption(label="Zamówienie-MC", emoji="⛏️"),
            discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨"),
            discord.SelectOption(label="Odbiór Nagrody", emoji="🎁")
        ]
    )
    async def callback(self, interaction, select):
        name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=name, overwrites=overwrites)
        emb = discord.Embed(title=f"Ticket: {select.values[0]}", description="Opisz swój problem.", color=THEME_COLOR)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Kanał: {ch.mention}", ephemeral=True)

# --- WERYFIKACJA ---

class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_btn")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)

# --- KOMENDY SLASH ---

@bot.tree.command(name="konkurs", description="Startuje konkurs")
@app_commands.checks.has_permissions(administrator=True)
async def konkurs_cmd(interaction):
    await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="weryfikacja", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_cmd(interaction):
    emb = discord.Embed(title="Weryfikacja 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", description="Kliknij przycisk!", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="ticket", description="Panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_cmd(interaction):
    emb = discord.Embed(title="Tickety 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", description="Wybierz kategorię z menu.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="clear", description="Usuwa wiadomości")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_cmd(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"✅ Usunięto {ilosc} wiadomości.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃"))
    print(f"✅ Bot online jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
