import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA ID ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x5865F2 # Klasyczny Blurple (elegancki i czysty)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Trwałość przycisków
        self.add_view(TicketLauncher())
        self.add_view(VerifyView())
        self.add_view(TicketControlView())

    async def on_ready(self):
        # Automatyczna synchronizacja komend slash
        await self.tree.sync()
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃"))
        print(f"✅ Bot zalogowany jako {self.user}")

bot = SwirHubBot()

# --- SYSTEM LOGOWANIA ---
async def send_log(title, description, color=discord.Color.blue()):
    channel = bot.get_channel(ID_KANALU_LOGI)
    if channel:
        emb = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        await channel.send(embed=emb)

# --- KOMENDA /TEKST (MODERN LOOK) ---
class TekstModal(Modal, title="🖋️ Nowe Ogłoszenie"):
    tytul = TextInput(label="Nagłówek", placeholder="Tytuł komunikatu...", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Wpisz treść ogłoszenia...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.tytul.value, description=self.tresc.value, color=THEME_COLOR)
        emb.set_footer(text=f"Wysłano przez: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie wysłane.", ephemeral=True)

@bot.tree.command(name="tekst", description="Tworzy estetyczne ogłoszenie")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

# --- SYSTEM TICKETÓW (CLEAN DESIGN) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij zgłoszenie", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="close_t_clean")
    async def close(self, interaction: discord.Interaction, button: Button):
        await send_log("🔒 Zamknięto Ticket", f"Kanał: `{interaction.channel.name}`\nPrzez: {interaction.user.mention}", color=discord.Color.red())
        await interaction.response.send_message("Kanał zostanie usunięty za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz temat pomocy...", custom_id="sel_t_clean", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
        discord.SelectOption(label="Pytania i Sklep", emoji="💳"),
        discord.SelectOption(label="Inne sprawy", emoji="📂")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ID_ROLI_ADMINISTRACJI): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        await send_log("📩 Nowy Ticket", f"Użytkownik: {interaction.user.mention}\nTemat: `{select.values[0]}`", color=discord.Color.green())
        
        emb = discord.Embed(title="Centrum Pomocy 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention},\nOpisz krótko swoją sprawę. Administracja odpowie tak szybko, jak to możliwe.\n\n**Temat:** `{select.values[0]}`"
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto ticket: {ch.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="Panel wsparcia")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="Potrzebujesz pomocy?", description="Jeśli masz problem lub pytanie, otwórz zgłoszenie wybierając temat z menu poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel wysłany.", ephemeral=True)

# --- WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.primary, custom_id="ver_clean")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano.", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction: discord.Interaction):
    emb = discord.Embed(title="Weryfikacja", description="Kliknij przycisk poniżej, aby otrzymać dostęp do reszty kanałów.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Wysłano.", ephemeral=True)

# --- KOMENDA SYNC ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Zsynchronizowano komendy slash.")

bot.run(os.getenv('DISCORD_TOKEN'))
