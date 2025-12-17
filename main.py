import discord
import os
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- 1. OKIENKO GUI (MODAL) ---
class RegulaminModal(Modal, title="Kreator Regulaminu"):
    tytul_input = TextInput(
        label="Tytuł Regulaminu",
        placeholder="np. REGULAMIN SERWERA",
        style=discord.TextStyle.short,
        required=True
    )

    opis_input = TextInput(
        label="Treść Zasad",
        placeholder="Wpisz punkty regulaminu...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Tworzymy czysty embed
        embed = discord.Embed(
            title=self.tytul_input.value,
            description=self.opis_input.value,
            color=0x2b589b
        )
        
        if interaction.guild.icon:
            embed.set_footer(text=f"Administracja {interaction.guild.name}", icon_url=interaction.guild.icon.url)
        else:
            embed.set_footer(text=f"Administracja {interaction.guild.name}")

        # Wysyłamy TYLKO regulamin na kanał
        await interaction.channel.send(embed=embed)
        
        # Potwierdzenie wysłania widoczne TYLKO dla Ciebie (zniknie samo)
        await interaction.response.send_message("Opublikowano!", ephemeral=True)

# --- 2. WIDOK PRZYCISKU ---
class RegulaminView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Stwórz Regulamin", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Brak uprawnień.", ephemeral=True)
            return
        await interaction.response.send_modal(RegulaminModal())

# --- 3. START I KOMENDY ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} gotowy!')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.message.delete() # Usuwa Twoje "!setup"
    # Wysyła sam przycisk, bez żadnego dodatkowego tekstu
    await ctx.send(view=RegulaminView())

# Uruchamianie
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
