import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from datetime import datetime

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956 # <--- MOŻESZ ZMIENIĆ NA INNE ID JEŚLI CHCESZ OSOBNY KANAŁ
THEME_COLOR = 0x9b59b6 # Fiolet SwirHub

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

bot = SwirHubBot()

# --- SYSTEM POWITAŃ (WŁĄCZONY) ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(
            title="👋 Witamy w 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!",
            description=f"Siema {member.mention}!\nCieszymy się, że wpadłeś na nasz serwer.\n\nZajrzyj na kanał weryfikacji, aby otrzymać pełny dostęp!",
            color=THEME_COLOR,
            timestamp=datetime.now()
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=f"Jesteś naszym {len(member.guild.members)} członkiem!")
        
        await channel.send(content=f"Cześć {member.mention}!", embed=emb)

# --- SYSTEM TICKETÓW (Z LOGAMI) ---
class TicketControlView(View):
    def __init__(self): 
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        log_channel = bot.get_channel(ID_KANALU_LOGI)
        if log_channel:
            embed_log = discord.Embed(
                title="🔒 Ticket Zamknięty",
                description=f"Kanał: **{interaction.channel.name}**",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed_log.add_field(name="Zamknięty przez:", value=f"{interaction.user.mention} ({interaction.user.id})")
            await log_channel.send(embed=embed_log)

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
        super().__init__(placeholder="Wybierz kategorię zgłoszenia...", options=options, custom_id="t_sel")

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
        
        log_channel = bot.get_channel(ID_KANALU_LOGI)
        if log_channel:
            log_emb = discord.Embed(
                title="🎫 Nowy Ticket",
                description=f"Użytkownik {interaction.user.mention} otworzył zgłoszenie: {ch.mention}\nKategoria: **{self.values[0]}**",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=log_emb)

        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
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
            return await interaction.response.send_message("❌ Błąd: Nie znaleziono roli!", ephemeral=True)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zostałeś zweryfikowany w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Błąd: Nie mogę nadać roli. Sprawdź moje uprawnienia!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="verify_setup", description="Wysyła panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja",
        description="Aby uzyskać dostęp do serwera, musisz się zweryfikować.\n\nKliknij przycisk poniżej, aby otrzymać rolę.",
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel weryfikacji wysłany!", ephemeral=True)

@bot.tree.command(name="ticket_setup", description="Wysyła panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY",
        description="Masz pytanie lub chcesz coś zamówić? Wybierz odpowiednią kategorię z menu poniżej.",
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel ticketów wysłany!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend dla **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!")

# --- URUCHOMIENIE I STATUS ---
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"✅ Zalogowano jako {bot.user}")
    print(f"✅ Status: Ogląda 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
