import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672  # <--- WPISZ ID ROLI
ID_KANALU_POWITAN = 1451263521995362564    # <--- WPISZ ID KANAŁU

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków, aby przyciski działały po restarcie
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

bot = SwirHubBot()
THEME_COLOR = 0x9b59b6 # Fiolet SwirHub

# --- SYSTEM TICKETÓW (NOWE OPCJE) ---
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
            discord.SelectOption(label="Pomoc Ogólna", emoji="💎", description="Pytania i pomoc techniczna"),
            discord.SelectOption(label="Zamówienie-MC", emoji="⛏️", description="Zamówienia związane z Minecraft"),
            discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨", description="Projekty graficzne, boty, studio"),
            discord.SelectOption(label="Odbiór Nagrody", emoji="🎁", description="Jeśli coś wygrałeś!")
        ]
        super().__init__(placeholder="Wybierz jedną z opcji która Cię interesuje...", options=options, custom_id="t_sel")

    async def callback(self, interaction: discord.Interaction):
        name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=name, overwrites=overwrites)
        
        emb = discord.Embed(
            title=f"💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • {self.values[0]}", 
            description=f"Witaj {interaction.user.mention}!\nNapisz dokładnie, w czym możemy Ci pomóc, a administracja zaraz się pojawi.", 
            color=THEME_COLOR
        )
        await ch.send(content=f"{interaction.user.mention} | <@&ROLA_ADMINISTRACJI_ID>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Utworzono zgłoszenie: {ch.mention}", ephemeral=True)

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
        if not role:
            return await interaction.response.send_message("❌ Błąd: Nie znaleziono roli weryfikacyjnej!", ephemeral=True)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zostałeś pomyślnie zweryfikowany w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Bot nie może nadać roli. Sprawdź czy rola bota jest wyżej niż rola weryfikacyjna!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="verify_setup", description="Wysyła panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja",
        description="Aby uzyskać dostęp do serwera, musisz się zweryfikować.\n\nKliknij przycisk poniżej aby się zweryfikować.",
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)

@bot.tree.command(name="ticket_setup", description="Wysyła panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY",
        description=(
            "Jeśli potrzebujesz pomocy lub masz pytania, wybierz **Pomoc ogólną**.\n\n"
            "W sprawie zamówień lub wyceny skorzystaj z odpowiedniej kategorii w menu.\n"
            "Jeżeli jesteś kupującym, wysyłaj środki wyłącznie na dane podane przez bota.\n\n"
            "Administracja oraz Zespół proszą o niezakładanie zgłoszeń bez powodu i niepingowanie — odpowiemy, gdy tylko będziemy dostępni."
        ),
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel ticketów wysłany!", ephemeral=True)

# --- KOMENDA SYNCHRONIZACJI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    try:
        # Rejestruje komendy bezpośrednio na Twoim serwerze (natychmiastowe działanie)
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend slash dla **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!")
    except Exception as e:
        await ctx.send(f"❌ Błąd synchronizacji: {e}")

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
