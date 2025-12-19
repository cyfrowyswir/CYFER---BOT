import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA ID (SPRAWDŹ CZY SĄ DOBRE!) ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # To sprawia, że przyciski działają nawet po restarcie bota
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

    async def on_ready(self):
        total = sum(g.member_count for g in self.guilds)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🛸 {total} osób"))
        print(f"✅ SwirHub Bot GOTOWY")

bot = SwirHubBot()

# --- FUNKCJA LOGUJĄCA (BEZPIECZNA) ---
async def safe_log(title, description, color=0x3498db):
    try:
        channel = bot.get_channel(ID_KANALU_LOGI)
        if channel:
            emb = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
            await channel.send(embed=emb)
    except Exception as e:
        print(f"Błąd logowania: {e}")

# --- MODAL DLA KOMENDY /TEKST ---
class TekstModal(Modal, title="🖋️ Nowe Ogłoszenie"):
    tytul = TextInput(label="Tytuł", placeholder="Wpisz nagłówek...", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Twoja treść...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=f"📜 {self.tytul.value}", description=self.tresc.value, color=THEME_COLOR)
        emb.set_footer(text="Oficjalne ogłoszenie SwirHub")
        await interaction.channel.send(embed=emb)
        if not interaction.response.is_done():
            await interaction.response.send_message("✅ Wysłano!", ephemeral=True)

# --- SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="btn_close")
    async def close(self, interaction: discord.Interaction, button: Button):
        await safe_log("🔒 Ticket Zamknięty", f"Kanał: `{interaction.channel.name}`\nPrzez: {interaction.user.mention}")
        await interaction.response.send_message("Usuwanie kanału za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz powód zgłoszenia...", custom_id="sel_ticket", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
        discord.SelectOption(label="Sklep", emoji="💰"),
        discord.SelectOption(label="Inne", emoji="❓")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        # Uprawnienia: admin i użytkownik widzą, reszta nie
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ID_ROLI_ADMINISTRACJI): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        await safe_log("📩 Nowy Ticket", f"Użytkownik: {interaction.user.mention}\nTemat: {select.values[0]}")
        
        emb = discord.Embed(title="🏛️ POMOC SWIRHUB", description=f"Witaj {interaction.user.mention}!\nNapisz w czym możemy pomóc.\nTemat: **{select.values[0]}**", color=THEME_COLOR)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

# --- WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.success, emoji="✅", custom_id="btn_ver")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Zweryfikowano!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="tekst", description="Tworzy wiadomość w Embedzie")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="ticket", description="Panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="📩 POMOC I ZGŁOSZENIA", description="Wybierz odpowiednią kategorię poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Wysłano panel.", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction: discord.Interaction):
    emb = discord.Embed(title="✅ WERYFIKACJA", description="Kliknij przycisk, aby otrzymać rangę.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Wysłano weryfikację.", ephemeral=True)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Zsynchronizowano!")

bot.run(os.getenv('DISCORD_TOKEN'))
