import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1234567890 # WPISZ SWOJE ID
ID_KANALU_POWITAN = 1234567890   # WPISZ SWOJE ID

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix='!', intents=intents)
THEME_COLOR = 0x9b59b6

# --- TICKET SYSTEM ---
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
            discord.SelectOption(label="Zamówienie", emoji="🤖"),
            discord.SelectOption(label="Inne", emoji="📩")
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

# --- WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if not role:
            return await interaction.response.send_message("Błąd: Nie znaleziono roli. Sprawdź ID w kodzie!", ephemeral=True)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot nie ma uprawnień do nadawania ról (sprawdź hierarchię ról)!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="ticket_setup", description="Panel ticketów")
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY", description="Wybierz kategorię z menu poniżej.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=View().add_item(TicketSelect()))
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="verify_setup", description="Panel weryfikacji")
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja", description="Kliknij przycisk, aby się zweryfikować.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.command()
async def sync(ctx):
    fmt = await bot.tree.sync()
    await ctx.send(f"✅ Zsynchronizowano {len(fmt)} komend slash.")

@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(View().add_item(TicketSelect()))
    bot.add_view(TicketControlView())
    print(f"Bot {bot.user} online!")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
