import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 123456789012345678 # <--- ZMIEŃ NA ID ROLI ADMINA
THEME_COLOR = 0x9b59b6 # Fiolet SwirHub

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

# --- SYSTEM POWITAŃ ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(
            title="Witamy w 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!",
            description=f"Siema {member.mention}! Cieszymy się, że jesteś z nami.\nZajrzyj na kanał weryfikacji, aby otrzymać dostęp!",
            color=THEME_COLOR
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

# --- SYSTEM TICKETÓW ---
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
            await interaction.response.send_message("❌ Błąd uprawnień ról!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="verify_setup", description="Wysyła panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja",
        description="Aby uzyskać dostęp do serwera, musisz się zweryfikować.\n\nKliknij przycisk poniżej.",
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.tree.command(name="ticket_setup", description="Wysyła panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY",
        description="Wybierz kategorię z menu poniżej, aby otworzyć zgłoszenie.",
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend dla **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!")

# --- URUCHOMIENIE I STATUS ---
@bot.event
async def on_ready():
    # Ustawienie statusu: Ogląda 𝑺𝒘𝒊𝒓𝑯𝒖𝒃
    activity = discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"✅ Zalogowano jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
