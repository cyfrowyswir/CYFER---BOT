import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- ARTEFAKTY KONFIGURACJI ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956 # TWÓJ KANAŁ LOGÓW
THEME_COLOR = 0x9b59b6

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

    async def on_ready(self):
        print(f"✅ ZALOGOWANO JAKO: {self.user}")
        
        # --- TEST KANAŁU LOGÓW ---
        log_chan = self.get_channel(ID_KANALU_LOGI)
        if log_chan:
            print(f"📡 Kanał logów znaleziony: #{log_chan.name}")
            try:
                # Próba wysłania powitalnego logu po starcie
                emb = discord.Embed(title="⚔️ System Logów Aktywny", description="Kronikarz gotowy do spisywania dziejów.", color=0x2ecc71)
                await log_chan.send(embed=emb)
            except discord.Forbidden:
                print("❌ BŁĄD: Bot nie ma uprawnień do PISANIA na kanale logów!")
        else:
            print("❌ BŁĄD: Nie znaleziono kanału logów! Sprawdź czy ID jest poprawne i czy bot ma dostęp do kanału.")

bot = SwirHubBot()

# --- 📜 FUNKCJA LOGUJĄCA (Z DODATKOWĄ OCHRONĄ) ---
async def log_event(title, description, color=0x3498db):
    channel = bot.get_channel(ID_KANALU_LOGI)
    if channel:
        emb = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Records")
        try:
            await channel.send(embed=emb)
        except:
            print(f"⚠️ Nie udało się wysłać logu: {title}")

# --- 🏛️ SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t_v2")
    async def close(self, interaction: discord.Interaction, button: Button):
        await log_event("🔒 Audiencja Zakończona", f"Kanał: `{interaction.channel.name}`\nPrzez: {interaction.user.mention}", color=0xe74c3c)
        await interaction.response.send_message("🔒 Komnata zostanie usunięta za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="Wybierz temat pomocy...", custom_id="sel_t_v2", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
        discord.SelectOption(label="Sklep / Rangi", emoji="💎"),
        discord.SelectOption(label="Zgłoszenie/Skarga", emoji="⚖️")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        # Logowanie
        await log_event("📩 Nowa Audiencja", f"Wędrowiec: {interaction.user.mention}\nTemat: `{select.values[0]}`\nKanał: {ch.mention}")

        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\n\n**Temat:** `{select.values[0]}`\nOpisz swą sprawę, a Strażnicy (<@&{ID_ROLI_ADMINISTRACJI}>) wkrótce przybędą."
        
        await ch.send(embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

# --- 🛸 WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.success, emoji="✅", custom_id="v_btn_v2")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano!", ephemeral=True)

# --- ⚔️ KOMENDY SLASH (NAPRAWIONA SYNCHRONIZACJA) ---
@bot.tree.command(name="tekst", description="Tworzy Embed")
async def tekst(interaction: discord.Interaction):
    # Modal musi być wywołany przez interaction.response
    modal = TekstModal()
    await interaction.response.send_modal(modal)

class TekstModal(Modal, title="🖋️ Królewskie Ogłoszenie"):
    tytul = TextInput(label="Nagłówek", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, min_length=1)
    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=f"📜 {self.tytul.value}", description=self.tresc.value, color=THEME_COLOR)
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszono!", ephemeral=True)

@bot.tree.command(name="ticket", description="Panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="🆘 Centrum Pomocy", description="Wybierz kategorię z menu poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel gotowy.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend!")

bot.run(os.getenv('DISCORD_TOKEN'))
