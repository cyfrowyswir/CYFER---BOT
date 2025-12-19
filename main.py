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
THEME_COLOR = 0x5865F2

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
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃"))
        print(f"✅ Bot Gotowy: {self.user}")

bot = SwirHubBot()

# --- 🔥 KOMENDA NAPRAWCZA (USUWA DUPLIKATY) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    """Całkowite czyszczenie i ponowna rejestracja komend"""
    msg = await ctx.send("⏳ Czyszczenie bazy komend Discorda... (to może potrwać)")
    
    # 1. Czyścimy komendy globalne
    bot.tree.clear(guild=None)
    await bot.tree.sync(guild=None)
    
    # 2. Czyścimy komendy serwerowe
    bot.tree.clear(guild=ctx.guild)
    await bot.tree.sync(guild=ctx.guild)
    
    # 3. Rejestrujemy tylko jedną, świeżą kopię
    synced = await bot.tree.sync()
    
    await msg.edit(content=f"✅ **Baza wyczyszczona!** Zarejestrowano {len(synced)} czystych komend.\n**WAŻNE:** Zrestartuj teraz swojego Discorda (Ctrl+R), aby odświeżyć menu!")

# --- 🖋️ KOMENDA /TEKST ---
class TekstModal(Modal, title="Nowe Ogłoszenie"):
    tytul = TextInput(label="Nagłówek", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.tytul.value, description=self.tresc.value, color=THEME_COLOR)
        emb.set_footer(text=f"𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • {interaction.user.display_name}")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Wysłano.", ephemeral=True)

@bot.tree.command(name="tekst", description="Tworzy estetyczne ogłoszenie")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

# --- 🎟️ SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="c_1")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Usuwanie...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz temat...", custom_id="s_1", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
        discord.SelectOption(label="Inne", emoji="📂")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        emb = discord.Embed(title="Wsparcie", description=f"Opisz sprawę. Temat: **{select.values[0]}**", color=THEME_COLOR)
        await ch.send(embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="Panel wsparcia")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="Centrum Pomocy", description="Otwórz zgłoszenie poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Gotowe.", ephemeral=True)

# --- 🛸 WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.primary, custom_id="v_1")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano.", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction: discord.Interaction):
    emb = discord.Embed(title="Weryfikacja", description="Kliknij przycisk.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Gotowe.", ephemeral=True)

bot.run(os.getenv('DISCORD_TOKEN'))
