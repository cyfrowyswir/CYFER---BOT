import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KRÓLEWSKIE DEKRETY (ID) ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6

# --- KONFIGURACJA DUSZY BOTA ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # To sprawia, że przyciski NIE ZDYCHAJĄ po restarcie bota
        self.add_view(TicketLauncher())
        self.add_view(VerifyView())
        self.add_view(TicketControlView())

    async def on_ready(self):
        await self.tree.sync() # Automatyczna próba synchronizacji
        total = sum(g.member_count for g in self.guilds)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🛸 {total} dusz"))
        print(f"✅ KORONA OSADZONA: {self.user} DZIAŁA")

bot = SwirHubBot()

# --- 🛡️ FUNKCJA KRONIKARZA (LOGI) ---
async def wyslij_log(tytul, opis, kolor=0x3498db):
    try:
        kanal = bot.get_channel(ID_KANALU_LOGI)
        if kanal:
            emb = discord.Embed(title=tytul, description=opis, color=kolor, timestamp=datetime.now())
            await kanal.send(embed=emb)
    except:
        pass # Jeśli log zawiedzie, bot nie może się wywalić

# --- 🖋️ KOMENDA /TEKST (NAPRAWIONA) ---
class TekstModal(Modal, title="🖋️ Redagowanie Pisma"):
    tytul = TextInput(label="Nagłówek", placeholder="Tytuł Twojego ogłoszenia...", required=True)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Co chcesz ogłosić?", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=f"📜 {self.tytul.value}", description=self.tresc.value, color=THEME_COLOR)
        emb.set_footer(text=f"Przesłanie od: {interaction.user.display_name}")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Pismo wysłane!", ephemeral=True)

@bot.tree.command(name="tekst", description="Wysyła luksusowe ogłoszenie w ramce (Embed)")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

# --- 🎟️ SYSTEM AUDIENCJI (TICKETY) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Zakończ audiencję", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_final")
    async def close(self, interaction: discord.Interaction, button: Button):
        await wyslij_log("🔒 Zamknięto Ticket", f"Kanał: `{interaction.channel.name}`\nPrzez: {interaction.user.mention}", 0xe74c3c)
        await interaction.response.send_message("🔒 Zamykanie komnaty za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="Wybierz powód wizyty...", custom_id="select_ticket_final", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", value="techniczna"),
        discord.SelectOption(label="Skarbiec (Sklep)", emoji="💰", value="sklep"),
        discord.SelectOption(label="Skarga/Inne", emoji="⚖️", value="skarga")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        # Uprawnienia
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ID_ROLI_ADMINISTRACJI): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        await wyslij_log("📩 Nowy Ticket", f"Właściciel: {interaction.user.mention}\nTemat: `{select.values[0]}`\nKanał: {ch.mention}")
        
        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\nStrażnicy zostali wezwani. Opisz swoją sprawę.\n\n**Wybrany temat:** `{select.values[0]}`"
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="Tworzy panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="📩 CENTRUM POMOCY", description="Jeśli potrzebujesz wsparcia, wybierz kategorię z menu poniżej.", color=THEME_COLOR)
    emb.set_footer(text="System zgłoszeń SwirHub")
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel został postawiony.", ephemeral=True)

# --- 🛸 WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_final")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Przyznano dostęp!", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Tworzy panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction: discord.Interaction):
    emb = discord.Embed(title="🛸 WERYFIKACJA", description="Kliknij przycisk poniżej, aby wejść do królestwa.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Panel weryfikacji gotowy.", ephemeral=True)

# --- 🧹 PORZĄDKI ---
@bot.tree.command(name="clear", description="Usuwa wiadomości")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"🧹 Usunięto {ilosc} wiadomości.", ephemeral=True)

# --- 🔄 SYNCHRONIZACJA RĘCZNA ---
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Zsynchronizowano komendy!")

bot.run(os.getenv('DISCORD_TOKEN'))
