import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6 # Główny fiolet

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

    async def update_status(self):
        total = sum(g.member_count for g in self.guilds)
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"🛸 monitoruje {total} osób"
        ))

bot = SwirHubBot()

# --- MODAL: KONKURS (PIĘKNY WYGLĄD) ---
class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Biorę udział!", style=discord.ButtonStyle.secondary, emoji="✨", custom_id="join_g")
    async def join(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("🛡️ Spokojnie, Twój los już jest w urnie!", ephemeral=True)
        self.participants.append(interaction.user)
        emb = interaction.message.embeds[0]
        emb.set_footer(text=f"👥 Uczestników: {len(self.participants)} | 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        await interaction.message.edit(embed=emb)
        await interaction.response.send_message("🎯 Powodzenia! Twoje zgłoszenie zostało zapisane.", ephemeral=True)

class KonkursModal(Modal, title="🎁 Organizacja Wydarzenia"):
    nagroda = TextInput(label="Co chcesz rozdać?", placeholder="np. Ranga VIP na miesiąc", min_length=2)
    czas = TextInput(label="Czas trwania (s/m/h)", placeholder="np. 30m", max_length=5)
    opis = TextInput(label="Zasady / Wymagania", style=discord.TextStyle.paragraph, required=False, placeholder="np. Zaobserwuj nasze social media!")

    async def on_submit(self, interaction: discord.Interaction):
        units = {"s": 1, "m": 60, "h": 3600}
        match = re.match(r"(\d+)([smh])", self.czas.value.lower())
        if not match: return await interaction.response.send_message("❌ Błąd! Użyj formatu: 30s, 10m lub 2h.", ephemeral=True)
        
        seconds = int(match.group(1)) * units[match.group(2)]
        view = GiveawayView(timeout=seconds)
        
        emb = discord.Embed(title="✨ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 GIVEAWAY ✨", color=0xFFD700, timestamp=datetime.now())
        emb.set_thumbnail(url="https://i.imgur.com/vHqL3Y5.png") # Ikona prezentu
        emb.add_field(name="🏆 Nagroda", value=f"```yaml\n{self.nagroda.value}```", inline=False)
        if self.opis.value: emb.add_field(name="📜 Zasady", value=self.opis.value, inline=False)
        emb.add_field(name="⏰ Czas", value=f"Koniec za: `{self.czas.value}`", inline=True)
        emb.set_footer(text="Kliknij przycisk poniżej, aby dołączyć!")
        
        await interaction.response.send_message("✅ Konkurs został opublikowany!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        
        await asyncio.sleep(seconds)
        winner = random.choice(view.participants) if view.participants else None
        
        if winner:
            res = discord.Embed(title="🎊 MAMY ZWYCIĘZCĘ! 🎊", color=0x9b59b6, timestamp=datetime.now())
            res.description = f"Gratulacje {winner.mention}!\nWłaśnie wygrałeś: **{self.nagroda.value}**"
            res.set_footer(text="Skontaktuj się z administracją po odbiór!")
            await interaction.channel.send(content=f"🎉 Brawo {winner.mention}!", embed=res)
        else:
            await interaction.channel.send("😥 Niestety, tym razem nikt nie wziął udziału.")
        await msg.edit(view=None)

# --- SYSTEM TICKETÓW (PROJEKT PREMIUM) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.response.send_message("🗑️ Archiwizacja i usuwanie za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz temat rozmowy...", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Problemy z dostępem lub botem"),
        discord.SelectOption(label="Sklep & Płatności", emoji="💰", description="Pytania o rangi i zamówienia"),
        discord.SelectOption(label="Zgłoś gracza", emoji="🛡️", description="Ktoś łamie regulamin?")
    ])
    async def callback(self, interaction, select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        emb = discord.Embed(title="🔮 Centrum Wsparcia 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\nNasi moderatorzy zostali powiadomieni.\n\n> **Temat:** `{select.values[0]}`\n\nOpisz dokładnie swój problem poniżej."
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Support")
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Twój ticket: {ch.mention}", ephemeral=True)

# --- WERYFIKACJA (MINIMALIZM) ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.primary, emoji="🛸", custom_id="v_b")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("🛸 Weryfikacja udana! Witaj na pokładzie.", ephemeral=True)

# --- KOMENDY MODERACYJNE ---
@bot.tree.command(name="clear", description="Czyści niepotrzebne wiadomości")
@app_commands.checks.has_permissions(manage_messages=True)
async def clr(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    emb = discord.Embed(description=f"✨ **Magia!** Usunięto `{ilosc}` wiadomości.", color=THEME_COLOR)
    await interaction.response.send_message(embed=emb, ephemeral=True)

# --- KOMENDY KONFIGURACYJNE ---
@bot.tree.command(name="weryfikacja")
async def verif(interaction):
    emb = discord.Embed(title="🛸 WERYFIKACJA UŻYTKOWNIKÓW", color=THEME_COLOR)
    emb.description = "Aby zobaczyć resztę kanałów i stać się częścią **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**, kliknij w poniższy przycisk."
    emb.set_image(url="https://i.imgur.com/TwH3mS3.png") # Tutaj możesz dać banner serwera
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Opublikowano panel weryfikacji.", ephemeral=True)

@bot.tree.command(name="ticket")
async def tick(interaction):
    emb = discord.Embed(title="📩 POTRZEBUJESZ POMOCY?", color=THEME_COLOR)
    emb.description = "Otwórz bilet, aby skontaktować się bezpośrednio z naszą administracją."
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Opublikowano system ticketów.", ephemeral=True)

@bot.tree.command(name="konkurs")
async def conc(interaction): await interaction.response.send_modal(KonkursModal())

# --- EVENTY ---
@bot.event
async def on_member_join(member):
    await bot.update_status()
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="🪐 Nowa postać na orbicie!", color=THEME_COLOR)
        emb.description = f"Siema {member.mention}! Miło Cię widzieć w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**.\n\n> Nie zapomnij o weryfikacji!"
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_ready():
    await bot.update_status()
    print(f"🚀 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 AI jest aktywny!")

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Systemy zsynchronizowane.")

bot.run(os.getenv('DISCORD_TOKEN'))
