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
THEME_COLOR = 0x9b59b6

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
            name=f"monitoruje {total} osób"
        ))

bot = SwirHubBot()

# --- MODAL: KONKURS ---
class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Dołącz do konkursu!", style=discord.ButtonStyle.blurple, emoji="🎉", custom_id="join_give")
    async def join(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("❌ Już tu jesteś!", ephemeral=True)
        self.participants.append(interaction.user)
        emb = interaction.message.embeds[0]
        emb.set_footer(text=f"Uczestników: {len(self.participants)} • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        await interaction.message.edit(embed=emb)
        await interaction.response.send_message("✅ Zapisano Cię!", ephemeral=True)

class KonkursModal(Modal, title="✨ Tworzenie Konkursu"):
    nagroda = TextInput(label="Nagroda", placeholder="Co do wygrania?", min_length=1)
    czas = TextInput(label="Czas (np. 30s, 10m, 2h)", placeholder="1h", max_length=5)
    opis = TextInput(label="Dodatkowe informacje", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        units = {"s": 1, "m": 60, "h": 3600}
        match = re.match(r"(\d+)([smh])", self.czas.value.lower())
        if not match: return await interaction.response.send_message("❌ Błędny czas!", ephemeral=True)
        
        seconds = int(match.group(1)) * units[match.group(2)]
        view = GiveawayView(timeout=seconds)
        
        emb = discord.Embed(title="🎊 NOWY KONKURS 🎊", color=0xF1C40F, timestamp=datetime.now())
        emb.add_field(name="🎁 Nagroda", value=f"**{self.nagroda.value}**", inline=False)
        if self.opis.value: emb.add_field(name="📝 Info", value=self.opis.value, inline=False)
        emb.add_field(name="⏳ Czas", value=f"Zakończenie za: `{self.czas.value}`", inline=True)
        emb.set_footer(text="Uczestników: 0 • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        
        await interaction.response.send_message("🚀 Konkurs wystartował!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        
        await asyncio.sleep(seconds)
        winner = random.choice(view.participants) if view.participants else None
        
        if winner:
            res = discord.Embed(title="🏆 WYNIKI KONKURSU 🏆", color=0x2ECC71)
            res.description = f"Gratulacje {winner.mention}!\nWygrałeś: **{self.nagroda.value}**"
            await interaction.channel.send(content=winner.mention, embed=res)
        else:
            await interaction.channel.send(f"😥 Konkurs na **{self.nagroda.value}** zakończony bez uczestników.")
        await msg.edit(view=None)

# --- SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="c_t")
    async def close(self, interaction, button):
        emb = discord.Embed(description="🔒 Kanał zostanie usunięty za 5 sekund...", color=discord.Color.red())
        await interaction.response.send_message(embed=emb)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz powód zgłoszenia...", custom_id="t_s", options=[
        discord.SelectOption(label="Pomoc Ogólna", emoji="💎", description="Masz pytanie? Pisz tutaj!"),
        discord.SelectOption(label="Zamówienie", emoji="⛏️", description="Chcesz coś kupić? Zapraszamy."),
        discord.SelectOption(label="Współpraca", emoji="🤝", description="Chcesz z nami współpracować?")
    ])
    async def callback(self, interaction, select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        emb = discord.Embed(title="📩 Centrum Pomocy 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\nZaraz ktoś z <@&{ID_ROLI_ADMINISTRACJI}> Ci pomoże.\n\n**Kategoria:** `{select.values[0]}`"
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

# --- WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Potwierdzam regulamin", style=discord.ButtonStyle.success, emoji="✅", custom_id="v_b")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✨ Weryfikacja zakończona pomyślnie!", ephemeral=True)

# --- KOMENDY SLASH ---
@bot.tree.command(name="konkurs", description="Tworzy konkurs z przyciskiem")
@app_commands.checks.has_permissions(administrator=True)
async def concurso(interaction): await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="weryfikacja", description="Panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def verif(interaction):
    emb = discord.Embed(title="🛡️ System Weryfikacji", color=THEME_COLOR)
    emb.description = "Aby uzyskać dostęp do serwera **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**, kliknij przycisk poniżej."
    emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • Bezpieczeństwo")
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel gotowy!", ephemeral=True)

@bot.tree.command(name="ticket", description="Panel zgłoszeń")
@app_commands.checks.has_permissions(administrator=True)
async def tick(interaction):
    emb = discord.Embed(title="🎫 System Ticketów", color=THEME_COLOR)
    emb.description = "Potrzebujesz pomocy administracji?\nWybierz kategorię z menu poniżej."
    emb.set_image(url="https://i.imgur.com/vHqL3Y5.png") # Opcjonalne: ładny banner
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

@bot.tree.command(name="clear", description="Sprzątanie czatu")
@app_commands.checks.has_permissions(manage_messages=True)
async def clr(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    emb = discord.Embed(description=f"🧹 Usunięto **{ilosc}** wiadomości.", color=0x3498DB)
    await interaction.response.send_message(embed=emb, ephemeral=True)

# --- EVENTY ---
@bot.event
async def on_member_join(member):
    await bot.update_status()
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="✨ Nowy członek rodziny!", color=THEME_COLOR, timestamp=datetime.now())
        emb.description = f"Witaj {member.mention} na **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!\nZajrzyj na weryfikację."
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member): await bot.update_status()

@bot.event
async def on_ready():
    await bot.update_status()
    print(f"✅ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ONLINE")

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Komendy Slash zsynchronizowane!")

bot.run(os.getenv('DISCORD_TOKEN'))
