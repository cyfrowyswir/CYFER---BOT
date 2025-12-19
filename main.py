import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA ID (UPEWNIJ SIĘ, ŻE SĄ POPRAWNE) ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
THEME_COLOR = 0x9b59b6 # Fiolet SwirHub

# --- ZAAWANSOWANE UPRAWNIENIA ---
intents = discord.Intents.default()
intents.members = True          # Wymagane do powitań
intents.message_content = True  # Wymagane do komend !sync

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Rejestrujemy widoki, aby przyciski działały po restarcie
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())
        print("✅ Widoki (Views) załadowane pomyślnie.")

    async def on_ready(self):
        # Ustawienie statusu
        total_members = sum(guild.member_count for guild in self.guilds)
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"🛸 monitoruje {total_members} osób"
        ))
        print(f"✅ ZALOGOWANO JAKO: {self.user}")
        print("✅ System gotowy do pracy.")

bot = SwirHubBot()

# --- 1. NAPRAWIONY MODAL: /tekst ---
class TekstModal(Modal, title="🖋️ Królewskie Ogłoszenie"):
    tytul = TextInput(label="Tytuł", placeholder="Wpisz nagłówek...", min_length=1, max_length=100)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Co chcesz przekazać?", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        # Tworzenie pięknego Embedu
        emb = discord.Embed(
            title=f"📜 {self.tytul.value}", 
            description=f"\n{self.tresc.value}\n", 
            color=THEME_COLOR, 
            timestamp=datetime.now()
        )
        emb.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        emb.set_footer(text=f"Ogłoszenie od: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie opublikowane pomyślnie!", ephemeral=True)

# --- 2. MODAL: KONKURS ---
class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Dołączam!", style=discord.ButtonStyle.success, emoji="🎉", custom_id="join_giveaway_btn")
    async def join(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("🛡️ Już bierzesz udział!", ephemeral=True)
        
        self.participants.append(interaction.user)
        # Aktualizacja licznika w stopce
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"👥 Uczestników: {len(self.participants)} • Czas ucieka!")
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ Zapisano Cię do konkursu!", ephemeral=True)

class KonkursModal(Modal, title="🎁 Tworzenie Konkursu"):
    nagroda = TextInput(label="Nagroda", placeholder="np. Ranga VIP", max_length=100)
    czas_str = TextInput(label="Czas (s=sek, m=min, h=godz)", placeholder="np. 10m", max_length=5)
    opis = TextInput(label="Opis/Zasady", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Przeliczanie czasu
        multipliers = {"s": 1, "m": 60, "h": 3600}
        match = re.match(r"(\d+)([smh])", self.czas_str.value.lower())
        
        if not match:
            return await interaction.response.send_message("❌ Błędny format czasu! Użyj np. 30s, 5m, 1h.", ephemeral=True)

        seconds = int(match.group(1)) * multipliers[match.group(2)]
        
        # Tworzenie Embedu Konkursowego
        view = GiveawayView(timeout=seconds)
        emb = discord.Embed(title="🎉 WIELKI KONKURS 🎉", color=0xF1C40F, timestamp=datetime.now())
        emb.add_field(name="🏆 Nagroda", value=f"```fix\n{self.nagroda.value}```", inline=False)
        emb.add_field(name="⏳ Czas trwania", value=f"Zakończenie za: **{self.czas_str.value}**", inline=True)
        if self.opis.value:
            emb.add_field(name="📜 Zasady", value=f"> {self.opis.value}", inline=False)
        emb.set_footer(text="👥 Uczestników: 0 • Kliknij przycisk poniżej!")

        await interaction.response.send_message("✅ Konkurs wystartował!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        
        # Czekanie na koniec
        await asyncio.sleep(seconds)
        
        # Losowanie
        if view.participants:
            winner = random.choice(view.participants)
            win_emb = discord.Embed(title="🎊 MAMY ZWYCIĘZCĘ! 🎊", description=f"Gratulacje {winner.mention}!\nWygrywasz: **{self.nagroda.value}**", color=THEME_COLOR)
            await interaction.channel.send(content=f"{winner.mention}", embed=win_emb)
        else:
            await interaction.channel.send(f"😥 Nikt nie wziął udziału w konkursie na **{self.nagroda.value}**.")
        
        # Wyłączenie przycisku po czasie
        view.stop()
        await msg.edit(view=None)

# --- 3. TICKETY (Pełna naprawa) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close_btn")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Zgłoszenie zostanie zamknięte za 5 sekund...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="Wybierz temat pomocy...", custom_id="ticket_select_menu", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Problemy z serwerem/botem"),
        discord.SelectOption(label="Sklep / Rangi", emoji="💎", description="Pytania o zakupy"),
        discord.SelectOption(label="Współpraca", emoji="🤝", description="Propozycje partnerskie"),
        discord.SelectOption(label="Inne", emoji="❓", description="Pozostałe sprawy")
    ])
    async def callback(self, interaction: discord.Interaction, select: Select):
        # Ustawienia uprawnień
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Tworzenie kanału
        category = discord.utils.get(interaction.guild.categories, name="Tickety") # Opcjonalnie: szuka kategorii
        channel_name = f"ticket-{interaction.user.name}"
        
        channel = await interaction.guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        
        # Wiadomość w tickecie
        emb = discord.Embed(title="📩 Nowe Zgłoszenie", color=THEME_COLOR)
        emb.description = (f"Witaj {interaction.user.mention}!\n\n"
                           f"Wybrałeś temat: **{select.values[0]}**\n"
                           f"Administracja (<@&{ID_ROLI_ADMINISTRACJI}>) wkrótce Ci pomoże.\n"
                           "Opisz swój problem poniżej.")
        emb.set_footer(text="Aby zamknąć, kliknij kłódkę.")
        
        await channel.send(content=f"{interaction.user.mention}", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Utworzono zgłoszenie: {channel.mention}", ephemeral=True)

# --- 4. WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.primary, emoji="✅", custom_id="verify_btn_new")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano! Witamy.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli weryfikacyjnej. Skontaktuj się z adminem.", ephemeral=True)

# --- KOMENDY SLASH (REJESTRACJA) ---

@bot.tree.command(name="tekst", description="Wstawia eleganckie ogłoszenie (Embed)")
async def tekst(interaction: discord.Interaction):
    # To jest kluczowe dla naprawy błędu "nie działa":
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="konkurs", description="Rozpoczyna konkurs z nagrodami")
@app_commands.checks.has_permissions(administrator=True)
async def konkurs(interaction: discord.Interaction):
    await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="ticket", description="Wysyła panel ticketów na kanał")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    emb = discord.Embed(title="🆘 Centrum Pomocy", description="Potrzebujesz pomocy? Wybierz kategorię poniżej, aby otworzyć prywatny kanał z administracją.", color=THEME_COLOR)
    emb.add_field(name="⚠️ Uwaga", value="Nie otwieraj ticketów bez powodu.", inline=False)
    emb.set_image(url="https://media.discordapp.net/attachments/1008571062943719464/1098670868776607834/line.gif") # Elegancka linia
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel ticketów wysłany.", ephemeral=True)

@bot.tree.command(name="weryfikacja", description="Wysyła panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def weryfikacja(interaction: discord.Interaction):
    emb = discord.Embed(title="🛡️ Strefa Weryfikacji", description="Kliknij przycisk poniżej, aby uzyskać dostęp do serwera.", color=THEME_COLOR)
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Panel weryfikacji wysłany.", ephemeral=True)

@bot.tree.command(name="clear", description="Czyści wybraną ilość wiadomości")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"🧹 Usunięto {ilosc} wiadomości.", ephemeral=True)

# --- SYSTEM POWITAŃ ---
@bot.event
async def on_member_join(member):
    # Aktualizacja licznika
    total = sum(g.member_count for g in bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🛸 monitoruje {total} osób"))
    
    # Wiadomość powitalna
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title=f"Witaj w {member.guild.name}!", description=f"Cześć {member.mention}! Cieszymy się, że jesteś z nami.", color=THEME_COLOR)
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=f"Jesteś {member.guild.member_count}. osobą!")
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member):
    # Aktualizacja licznika przy wyjściu
    total = sum(g.member_count for g in bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"🛸 monitoruje {total} osób"))

# --- ⚠️ KLUCZOWE: KOMENDA DO SYNCHRONIZACJI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Ręczna synchronizacja komend - UŻYJ TEGO JEŚLI KOMENDY NIE DZIAŁAJĄ"""
    msg = await ctx.send("⏳ Synchronizacja komend w toku...")
    try:
        synced = await bot.tree.sync()
        await msg.edit(content=f"✅ Zsynchronizowano {len(synced)} komend! (Może to zająć chwilę zanim pojawią się w menu)")
        print(f"Zsynchronizowano komendy: {[c.name for c in synced]}")
    except Exception as e:
        await msg.edit(content=f"❌ Błąd synchronizacji: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
