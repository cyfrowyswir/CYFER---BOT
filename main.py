import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA ID ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956 # Kanał, gdzie trafią logi ticketów
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
        total = sum(g.member_count for g in self.guilds)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🛸 monitoruje {total} osób"))
        print(f"✅ SwirHub ONLINE")

bot = SwirHubBot()

# --- 📜 LOGOWANIE ZDARZEŃ ---
async def send_log(title, description, color=0x3498db):
    channel = bot.get_channel(ID_KANALU_LOGI)
    if channel:
        emb = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
        await channel.send(embed=emb)

# --- 🖋️ MODAL: /tekst ---
class TekstModal(Modal, title="🖋️ Królewskie Ogłoszenie"):
    tytul = TextInput(label="Nagłówek", placeholder="Tytuł...", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Twoje słowa...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=f"📜 {self.tytul.value}", description=self.tresc.value, color=THEME_COLOR, timestamp=datetime.now())
        emb.set_footer(text="Oficjalne Obwieszczenie SwirHub")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Wysłano!", ephemeral=True)

# --- 🏛️ TICKETY Z LOGAMI ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close(self, interaction: discord.Interaction, button: Button):
        await send_log("🔒 Zamknięto Audiencję", f"Komnata: `{interaction.channel.name}`\nZamknięta przez: {interaction.user.mention}", color=0xe74c3c)
        await interaction.response.send_message("🔒 Komnata zostanie usunięta za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="Wybierz temat...", custom_id="sel_t", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
        discord.SelectOption(label="Sklep / Rangi", emoji="💎"),
        discord.SelectOption(label="Zgłoszenie", emoji="⚖️")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        # Logowanie otwarcia
        await send_log("📩 Nowa Audiencja", f"Użytkownik: {interaction.user.mention}\nTemat: `{select.values[0]}`\nKanał: {ch.mention}")

        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\nWybrałeś temat: **{select.values[0]}**.\nOpisz sprawę, a administracja przybędzie."
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

# --- RESZTA KOMEND ---
@bot.tree.command(name="tekst", description="Tworzy Embed")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="ticket", description="Panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="🆘 Centrum Pomocy", description="Wybierz kategorię poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Wysłano.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend!")

bot.run(os.getenv('DISCORD_TOKEN'))
