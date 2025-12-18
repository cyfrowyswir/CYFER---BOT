import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6 # Fiolet SwirHub

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

bot = SwirHubBot()

# --- MODAL DO WYSYŁANIA TEKSTU (UI) ---
class TekstModal(Modal, title="Stwórz Embed 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    tytul = TextInput(label="Tytuł", placeholder="Wpisz tytuł ogłoszenia...", required=True)
    opis = TextInput(label="Opis", placeholder="Wpisz treść wiadomości...", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title=self.tytul.value,
            description=self.opis.value,
            color=THEME_COLOR,
            timestamp=datetime.now()
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Wysłano ogłoszenie!", ephemeral=True)

# --- SYSTEM POWITAŃ ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(
            title="👋 Witamy w 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!",
            description=f"Siema {member.mention}!\nZajrzyj na kanał weryfikacji!",
            color=THEME_COLOR
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

# --- SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        log_ch = bot.get_channel(ID_KANALU_LOGI)
        if log_ch:
            log_emb = discord.Embed(title="🔒 Ticket Zamknięty", color=discord.Color.red(), timestamp=datetime.now())
            log_emb.add_field(name="Zamknięty przez:", value=interaction.user.mention)
            await log_ch.send(embed=log_emb)
        await interaction.response.send_message("🔒 Usuwanie za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
            discord.SelectOption(label="Zamówienie-MC", emoji="⛏️"),
            discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨"),
            discord.SelectOption(label="Odbiór Nagrody", emoji="🎁")
        ]
        super().__init__(placeholder="Wybierz kategorię...", options=options, custom_id="t_sel")

    async def callback(self, interaction: discord.Interaction):
        name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=name, overwrites=overwrites)
        emb = discord.Embed(title=f"💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • {self.values[0]}", description="Napisz w czym możemy pomóc.", color=THEME_COLOR)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- SYSTEM WERYFIKACJI ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)

# --- KOMENDY SLASH ---

@bot.tree.command(name="tekst", description="Otwiera UI do wysłania własnego tekstu w Embedzie")
@app_commands.checks.has_permissions(administrator=True)
async def tekst(interaction: discord.Interaction):
    # Otwiera okno modalne
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="regulamin", description="Wysyła regulamin serwera")
@app_commands.checks.has_permissions(administrator=True)
async def regulamin(interaction: discord.Interaction):
    emb = discord.Embed(title="📜 Regulamin 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", description="1. Szacunek\n2. Brak spamu\n3. Zakaz reklam.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb)
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="verify_setup", description="Wysyła panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja", description="Kliknij przycisk poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.tree.command(name="ticket_setup", description="Wysyła panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY", description="Wybierz kategorię.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend.")

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"✅ Gotowy: {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
