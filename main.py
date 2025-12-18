import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1234567890 
ID_KANALU_POWITAN = 1234567890   

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True

# Definiujemy bota
class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków (żeby przyciski działały po restarcie)
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())
        
        # Automatyczna synchronizacja przy starcie (opcjonalnie, ale pomaga)
        # await self.tree.sync() 

bot = SwirHubBot()
THEME_COLOR = 0x9b59b6

# --- KOMPONENTY UI ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Usuwanie kanału za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
            discord.SelectOption(label="Zamówienie", emoji="🤖")
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
        emb = discord.Embed(title=f"Zgłoszenie: {self.values[0]}", description="Opisz swoją sprawę.", color=THEME_COLOR)
        await ch.send(content=interaction.user.mention, embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Utworzono: {ch.mention}", ephemeral=True)

class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Błąd ról (sprawdź hierarchię)!", ephemeral=True)

# --- SLASH COMMANDS ---
@bot.tree.command(name="ticket_setup", description="Panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY", description="Wybierz kategorię z menu poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.tree.command(name="verify_setup", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja", description="Kliknij przycisk poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

# --- KOMENDA RATUNKOWA (WPISZ !sync) ---
@bot.command()
async def sync(ctx):
    try:
        # To wymusza rejestrację komend na Twoim konkretnym serwerze (działa szybciej)
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend dla tego serwera!")
    except Exception as e:
        await ctx.send(f"❌ Błąd synchronizacji: {e}")

@bot.event
async def on_ready():
    print(f"✅ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Bot online jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
