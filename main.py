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
THEME_COLOR = 0x9b59b6 # Królewski fiolet

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków dla trwałości przycisków
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

# --- 📜 MODAL: PISMO KRÓLEWSKIE (/tekst) ---
class TekstModal(Modal, title="🖋️ Redagowanie Pisma"):
    tytul = TextInput(label="Nagłówek", placeholder="Wpisz tytuł...", min_length=1)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Twoje przesłanie...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title=f"📜 {self.tytul.value}", 
            description=f"\n{self.tresc.value}\n", 
            color=THEME_COLOR, 
            timestamp=datetime.now()
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • Oficjalny Dekret")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Pismo zostało rozesłane!", ephemeral=True)

# --- 🎁 IGRZYSKA (KONKURSY) ---
class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Biorę udział!", style=discord.ButtonStyle.secondary, emoji="✨", custom_id="join_g")
    async def join(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("🛡️ Już jesteś na liście!", ephemeral=True)
        self.participants.append(interaction.user)
        emb = interaction.message.embeds[0]
        emb.set_footer(text=f"👥 Uczestników: {len(self.participants)} | 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        await interaction.message.edit(embed=emb)
        await interaction.response.send_message("🎯 Twoje imię zapisano w zwojach!", ephemeral=True)

class KonkursModal(Modal, title="🎁 Organizacja Igrzysk"):
    nagroda = TextInput(label="Nagroda", placeholder="np. Ranga VIP", min_length=1)
    czas = TextInput(label="Czas (s/m/h)", placeholder="np. 1h", max_length=5)
    opis = TextInput(label="Zasady", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        units = {"s": 1, "m": 60, "h": 3600}
        match = re.match(r"(\d+)([smh])", self.czas.value.lower())
        if not match: return await interaction.response.send_message("❌ Zły czas!", ephemeral=True)
        
        seconds = int(match.group(1)) * units[match.group(2)]
        view = GiveawayView(timeout=seconds)
        emb = discord.Embed(title="✨ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 GIVEAWAY ✨", color=0xFFD700, timestamp=datetime.now())
        emb.add_field(name="🏆 Nagroda", value=f"```fix\n{self.nagroda.value}```", inline=False)
        if self.opis.value: emb.add_field(name="📜 Zasady", value=f"> {self.opis.value}", inline=False)
        emb.set_footer(text="Kliknij ✨, aby dołączyć!")
        
        await interaction.response.send_message("🚀 Igrzyska rozpoczęte!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        await asyncio.sleep(seconds)
        
        winner = random.choice(self.participants) if self.participants else None
        if winner:
            res = discord.Embed(title="🎊 MAMY ZWYCIĘZCĘ! 🎊", color=THEME_COLOR, description=f"Los wskazał na {winner.mention}!\nNagroda: **{self.nagroda.value}**")
            await interaction.channel.send(content=f"🎉 Gratulacje {winner.mention}!", embed=res)
        else:
            await interaction.channel.send("😥 Igrzyska zakończone bez chętnych.")
        await msg.edit(view=None)

# --- 🏛️ AUDIENCJA (UPRAWDZIWIONE TICKETY) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zakończ audiencję", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Komnata zostanie zapieczętowana za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz powód audiencji...", custom_id="t_select", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Gdy mechanizmy krainy zawodzą"),
        discord.SelectOption(label="Skarbiec (Zamówienia)", emoji="💰", description="Wymiana złota na cenne rangi"),
        discord.SelectOption(label="Przymierze (Współpraca)", emoji="🤝", description="Dla poszukujących sojuszu")
    ])
    async def callback(self, interaction, select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = (
            f"Witaj, wędrowcze {interaction.user.mention}.\n"
            "Strażnicy Skarbca zostali powiadomieni o Twoim przybyciu.\n\n"
            f"**Powód:** `{select.values[0]}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "> Opisz swą prośbę cierpliwie, a pomoc nadejdzie."
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • System Audiencji")
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto komnatę: {ch.mention}", ephemeral=True)

# --- 🛸 WERYFIKACJA ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.primary, emoji="🛸", custom_id="v_b")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🛸 Weryfikacja udana. Witaj w królestwie!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd konfiguracji roli.", ephemeral=True)

# --- ⚔️ KOMENDY SLASH (CZYSTY KODEKS) ---

@bot.tree.command(name="tekst", description="Redaguje oficjalne pismo królestwa")
async def tekst_cmd(interaction: discord.Interaction):
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="weryfikacja", description="Rozstawia bramę weryfikacyjną")
@app_commands.checks.has_permissions(administrator=True)
async def verif_cmd(interaction: discord.Interaction):
    emb = discord.Embed(
        title="🛸 BRAMA WERYFIKACYJNA", 
        description="Aby ujrzeć pełnię królestwa **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**, dotknij poniższego symbolu.", 
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("✅ Brama postawiona.", ephemeral=True)

@bot.tree.command(name="ticket", description="Tworzy panel audiencji")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_cmd(interaction: discord.Interaction):
    emb = discord.Embed(
        title="📩 POTRZEBUJESZ POMOCY?", 
        description=(
            "Otwórz bilet, aby skontaktować się z Radą Administracji.\n"
            "Wybierz temat z menu poniżej, by rozpocząć audiencję."
        ), 
        color=THEME_COLOR
    )
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel audiencji gotowy.", ephemeral=True)

@bot.tree.command(name="konkurs", description="Rozpoczyna wielkie igrzyska")
@app_commands.checks.has_permissions(administrator=True)
async def conc_cmd(interaction: discord.Interaction):
    await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="clear", description="Usuwa zbędny pył słów")
@app_commands.checks.has_permissions(manage_messages=True)
async def clr_cmd(interaction: discord.Interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    emb = discord.Embed(description=f"🧹 Usunięto **{ilosc}** zbędnych pism.", color=THEME_COLOR)
    await interaction.response.send_message(embed=emb, ephemeral=True)

# --- 📜 ZDARZENIA ---
@bot.event
async def on_member_join(member):
    await bot.update_status()
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="🪐 Nowa dusza w królestwie!", color=THEME_COLOR)
        emb.description = f"Witaj {member.mention}! Niech Twoja podróż przez **𝑺𝒘𝒊𝒓𝑯𝒖𝒃** będzie owocna."
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member): await bot.update_status()

@bot.event
async def on_ready():
    await bot.update_status()
    print(f"✅ SwirHub ONLINE i gotowy do służby.")

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Kodeks komend Slash został odświeżony!")

bot.run(os.getenv('DISCORD_TOKEN'))
