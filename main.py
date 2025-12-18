import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime, timedelta

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
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

# --- MODAL DO KONKURSU ---
class KonkursModal(Modal, title="Uruchom Konkurs 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    nagroda = TextInput(label="Nagroda", placeholder="Co jest do wygrania?", required=True)
    opis = TextInput(label="Opis / Zasady", placeholder="Opisz zasady...", style=discord.TextStyle.paragraph, required=True)
    czas = TextInput(label="Czas trwania", placeholder="Np. 24h", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title="🎉 NOWY KONKURS 🎉", description=f"**Nagroda:** {self.nagroda.value}\n\n**Zasady:**\n{self.opis.value}\n\n**Czas:** {self.czas.value}", color=discord.Color.gold(), timestamp=datetime.now())
        emb.set_footer(text="Powodzenia!")
        await interaction.channel.send(content="@everyone", embed=emb)
        await interaction.response.send_message("✅ Wysłano!", ephemeral=True)

# --- MODAL DO TEKSTU ---
class TekstModal(Modal, title="Stwórz Embed 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    tytul = TextInput(label="Tytuł", required=True)
    opis = TextInput(label="Treść", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.tytul.value, description=self.opis.value, color=THEME_COLOR, timestamp=datetime.now())
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Wysłano!", ephemeral=True)

# --- KOMENDY MODERACYJNE ---

@bot.tree.command(name="kick", description="Wyrzuca użytkownika z serwera")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak powodu"):
    await uzytkownik.kick(reason=powod)
    emb = discord.Embed(title="👢 Wyrzucono użytkownika", color=discord.Color.orange(), timestamp=datetime.now())
    emb.add_field(name="Użytkownik:", value=uzytkownik.mention)
    emb.add_field(name="Moderator:", value=interaction.user.mention)
    emb.add_field(name="Powód:", value=powod)
    await interaction.response.send_message(f"✅ Wyrzucono {uzytkownik.mention}", ephemeral=True)
    await bot.get_channel(ID_KANALU_LOGI).send(embed=emb)

@bot.tree.command(name="ban", description="Banuje użytkownika na serwerze")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, uzytkownik: discord.User, powod: str = "Brak powodu"):
    await interaction.guild.ban(uzytkownik, reason=powod)
    emb = discord.Embed(title="🔨 Zbanowano użytkownika", color=discord.Color.red(), timestamp=datetime.now())
    emb.add_field(name="Użytkownik:", value=uzytkownik.mention)
    emb.add_field(name="Moderator:", value=interaction.user.mention)
    emb.add_field(name="Powód:", value=powod)
    await interaction.response.send_message(f"✅ Zbanowano {uzytkownik.mention}", ephemeral=True)
    await bot.get_channel(ID_KANALU_LOGI).send(embed=emb)

@bot.tree.command(name="mute", description="Wycisza użytkownika (Time-out)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, uzytkownik: discord.Member, minuty: int, powod: str = "Brak powodu"):
    czas = timedelta(minutes=minuty)
    await uzytkownik.timeout(czas, reason=powod)
    await interaction.response.send_message(f"✅ Wyciszono {uzytkownik.mention} na {minuty} min.", ephemeral=True)
    
    emb = discord.Embed(title="🔇 Wyciszono użytkownika", color=discord.Color.light_grey(), timestamp=datetime.now())
    emb.add_field(name="Kto:", value=uzytkownik.mention); emb.add_field(name="Czas:", value=f"{minuty}m"); emb.add_field(name="Powód:", value=powod)
    await bot.get_channel(ID_KANALU_LOGI).send(embed=emb)

@bot.tree.command(name="unmute", description="Zdejmuje wyciszenie")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, uzytkownik: discord.Member):
    await uzytkownik.timeout(None)
    await interaction.response.send_message(f"✅ Odciszono {uzytkownik.mention}", ephemeral=True)

@bot.tree.command(name="clear", description="Usuwa określoną liczbę wiadomości")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, ilosc: int):
    if ilosc > 100:
        return await interaction.response.send_message("❌ Maksymalnie 100 wiadomości na raz!", ephemeral=True)
    
    deleted = await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"✅ Usunięto {len(deleted)} wiadomości.", ephemeral=True)
    
    emb = discord.Embed(title="🧹 Wyczyścono czat", color=discord.Color.blue(), timestamp=datetime.now())
    emb.add_field(name="Kanał:", value=interaction.channel.mention)
    emb.add_field(name="Ilość:", value=f"{len(deleted)}")
    emb.add_field(name="Moderator:", value=interaction.user.mention)
    await bot.get_channel(ID_KANALU_LOGI).send(embed=emb)

# --- RESZTA SYSTEMÓW (TICKETY, WERYFIKACJA) ---

class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_t")
    async def close_ticket(self, interaction, button):
        await interaction.response.send_message("🔒 Usuwanie za 5s...")
        await asyncio.sleep(5); await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz kategorię...", options=[
        discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
        discord.SelectOption(label="Zamówienie-MC", emoji="⛏️"),
        discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨"),
        discord.SelectOption(label="Odbiór Nagrody", emoji="🎁")
    ], custom_id="t_sel")
    async def callback(self, interaction, select):
        name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        ch = await interaction.guild.create_text_channel(name=name, overwrites=overwrites)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=discord.Embed(title=f"Ticket: {select.values[0]}", color=THEME_COLOR), view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)

# --- SETUP KOMEND ---

@bot.tree.command(name="konkurs")
async def cmd_konkurs(interaction): await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="tekst")
async def cmd_tekst(interaction): await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="weryfikacja")
async def cmd_v(interaction): await interaction.channel.send(view=VerifyView()); await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="ticket")
async def cmd_t(interaction): await interaction.channel.send(view=TicketLauncher()); await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.command()
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"✅ Zsynchronizowano {len(synced)} komend.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃"))
    print(f"✅ Bot Gotowy!")

bot.run(os.getenv('DISCORD_TOKEN'))
