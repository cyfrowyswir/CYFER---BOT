import discord
import os
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- 1. WYGLĄD OKIENKA (MODAL) ---
class RegulaminModal(Modal, title="Kreator Regulaminu"):
    # Pole na tytuł (krótkie)
    tytul_input = TextInput(
        label="Tytuł Regulaminu",
        placeholder="np. REGULAMIN SERWERA",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )

    # Pole na treść (długie, wieloliniowe)
    opis_input = TextInput(
        label="Treść Zasad",
        placeholder="Wpisz tutaj punkty regulaminu...",
        style=discord.TextStyle.paragraph, # To pozwala na długi tekst i enter
        required=True,
        max_length=4000
    )

    # Co się dzieje po kliknięciu "Wyślij" w okienku
    async def on_submit(self, interaction: discord.Interaction):
        # Tworzymy ładną ramkę z tego, co wpisałeś
        embed = discord.Embed(
            title=self.tytul_input.value,
            description=self.opis_input.value,
            color=0x2b589b # Twój niebieski kolor
        )
        
        # Dodajemy stopkę
        if interaction.guild.icon:
            embed.set_footer(text=f"Administracja {interaction.guild.name}", icon_url=interaction.guild.icon.url)
        else:
            embed.set_footer(text=f"Administracja {interaction.guild.name}")

        # Wysyłamy gotowy regulamin na kanał
        await interaction.channel.send(embed=embed)
        
        # Potwierdzenie tylko dla Ciebie (nikt inny tego nie widzi)
        await interaction.response.send_message("✅ Regulamin został opublikowany!", ephemeral=True)

# --- 2. PRZYCISK OTWIERAJĄCY OKNO ---
class RegulaminView(View):
    def __init__(self):
        super().__init__(timeout=None) # Przycisk nie znika

    @discord.ui.button(label="📝 Stwórz Regulamin", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: Button):
        # Sprawdzamy czy klikający ma admina
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Nie masz uprawnień!", ephemeral=True)
            return
            
        # Otwieramy okienko (Modal)
        await interaction.response.send_modal(RegulaminModal())

# --- 3. START BOTA ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} jest online!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

# Komenda, która wywołuje przycisk do tworzenia
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.message.delete() # Usuwa komendę !setup
    await ctx.send("Kliknij poniżej, aby otworzyć kreator regulaminu:", view=RegulaminView())

# Uruchamianie
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
