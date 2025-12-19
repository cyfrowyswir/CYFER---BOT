import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- ⚙️ KONFIGURACJA ID ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x2f3136 # Elegancki ciemny antracyt
GOLD_COLOR = 0xd4af37  # Złoty akcent

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Rejestracja widoków (żeby przyciski zawsze działały)
        self.add_view(TicketLauncher())
        self.add_view(VerifyView())
        self.add_view(TicketControlView())

    async def on_ready(self):
        # WYMUSZONA SYNCHRONIZACJA KOMEND
        try:
            print("⏳ Odświeżanie bazy komend Slash...")
            synced = await self.tree.sync()
            print(f"✅ Sukces! Zsynchronizowano {len(synced)} komend.")
        except Exception as e:
            print(f"❌ Błąd synchronizacji: {e}")
            
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Luxury"
        ))
        print(f"🛡️ System 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Online: {self.user}")

bot = SwirHubBot()

# --- 📜 SYSTEM LOGOWANIA ---
async def safe_log(title, description, color=0x3498db):
    channel = bot.get_channel(ID_KANALU_LOGI)
    if channel:
        emb = discord.Embed(title=f"📋 LOG: {title}", description=description, color=color, timestamp=datetime.now())
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Internal Logs")
        await channel.send(embed=emb)

# --- 🖋️ WIZUALKA: /TEKST ---
class TekstModal(Modal, title="📝 Tworzenie Ogłoszenia SwirHub"):
    tytul = TextInput(label="Nagłówek ogłoszenia", placeholder="Wpisz tytuł...", min_length=1)
    tresc = TextInput(label="Treść ogłoszenia", style=discord.TextStyle.paragraph, placeholder="Twoja wiadomość...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(color=GOLD_COLOR, timestamp=datetime.now())
        emb.set_author(name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • OFICJALNY KOMUNIKAT", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        emb.title = f"✨ {self.tytul.value}"
        emb.description = f"\n{self.tresc.value}\n"
        emb.set_footer(text=f"Nadawca: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie wysłane z klasą!", ephemeral=True)

@bot.tree.command(name="tekst", description="Tworzy prestiżowe ogłoszenie")
async def tekst(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

# --- 🎟️ WIZUALKA: TICKETY ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ZAKOŃCZ AUDIENCJĘ", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_hub_v1")
    async def close(self, interaction: discord.Interaction, button: Button):
        await safe_log("Audiencja Zamknięta", f"Kanał: `{interaction.channel.name}`\nPrzez: {interaction.user.mention}", 0xff4d4d)
        await interaction.response.send_message("🔒 **Protokół zamknięcia aktywowany.** Kanał zniknie za 5s.")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="💎 Wybierz cel swojego zgłoszenia...", custom_id="select_hub_v1", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Problemy z serwerem lub kontem"),
        discord.SelectOption(label="Sklep i Płatności", emoji="💰", description="Rangi, dary i wsparcie finansowe"),
        discord.SelectOption(label="Współpraca / Reklama", emoji="🤝", description="Dla partnerów i twórców"),
        discord.SelectOption(label="Skarga / Zgłoszenie", emoji="⚖️", description="Zgłoś naruszenie zasad")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(ID_ROLI_ADMINISTRACJI): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        await safe_log("Otwarto Ticket", f"Użytkownik: {interaction.user.mention}\nTemat: `{select.values[0]}`", 0x2ecc71)
        
        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = (
            f"Witaj **{interaction.user.name}**!\n\n"
            "Twoje zgłoszenie zostało zarejestrowane w systemie **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**.\n"
            f"• Temat zgłoszenia: **{select.values[0]}**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Czekaj cierpliwie na odpowiedź kogoś z <@&{ID_ROLI_ADMINISTRACJI}>.\n"
            "Możesz już teraz opisać swój problem."
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Support • Wybierz przycisk poniżej, aby zamknąć.")
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Twoja audiencja została otwarta: {ch.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="Generuje panel wsparcia")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="📩 CENTRUM POMOCY 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
    emb.description = (
        "Potrzebujesz pomocy lub chcesz coś zgłosić?\n\n"
        "1️⃣ Wybierz odpowiednią kategorię z listy poniżej.\n"
        "2️⃣ Poczekaj na otwarcie prywatnego kanału.\n"
        "3️⃣ Opisz dokładnie swój problem."
    )
    emb.set_image(url="https://i.imgur.com/vHq7p0M.png") # Elegancka grafika (jeśli masz swoją, podmień link)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel ticketów został rozstawiony.", ephemeral=True)

# --- 🛡️ WIZUALKA: WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ODBIERZ DOSTĘP", style=discord.ButtonStyle.success, emoji="🛡️", custom_id="ver_hub_v1")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✨ Twoja obecność została potwierdzona. Witaj w krainie!", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Generuje panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction: discord.Interaction):
    emb = discord.Embed(title="🛸 BRAMA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
    emb.description = (
        "Aby uzyskać dostęp do ukrytych komnat serwera,\n"
        "musisz przejść krótką weryfikację.\n\n"
        "**Kliknij przycisk poniżej, aby wejść!**"
    )
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Brama została ustawiona.", ephemeral=True)

# --- 🧹 SYSTEM CLEAR ---
@bot.tree.command(name="clear", description="Oczyszcza czat")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"🧹 Pomyślnie usunięto **{ilosc}** wiadomości.", ephemeral=True)

# --- 🔄 KOMENDA SYNCHRONIZACJI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("💎 **Pomyślnie zsynchronizowano bazę danych komend Slash!**")

bot.run(os.getenv('DISCORD_TOKEN'))
