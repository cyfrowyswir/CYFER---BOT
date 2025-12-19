import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- ARTEFAKTY KONFIGURACJI 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
ID_KANALU_LOGI = 1451263526848167956
THEME_COLOR = 0x9b59b6 # Królewski fiolet

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Pieczęcie trwałości - przyciski działają po restarcie
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

# --- 🎁 WIELKIE IGRZYSKA (KONKURSY) ---
class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Biorę udział!", style=discord.ButtonStyle.secondary, emoji="✨", custom_id="join_give")
    async def join(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("🛡️ Twój los już spoczywa w urnie!", ephemeral=True)
        self.participants.append(interaction.user)
        emb = interaction.message.embeds[0]
        emb.set_footer(text=f"👥 Uczestników: {len(self.participants)} | 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
        await interaction.message.edit(embed=emb)
        await interaction.response.send_message("🎯 Powodzenia, wędrowcze!", ephemeral=True)

class KonkursModal(Modal, title="🎁 Organizacja Igrzysk"):
    nagroda = TextInput(label="Co chcesz podarować?", placeholder="np. Ranga VIP", min_length=1)
    czas = TextInput(label="Czas trwania (s/m/h)", placeholder="np. 1h", max_length=5)
    opis = TextInput(label="Zasady", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        units = {"s": 1, "m": 60, "h": 3600}
        match = re.match(r"(\d+)([smh])", self.czas.value.lower())
        if not match: return await interaction.response.send_message("❌ Zły format czasu!", ephemeral=True)
        
        seconds = int(match.group(1)) * units[match.group(2)]
        view = GiveawayView(timeout=seconds)
        
        emb = discord.Embed(title="✨ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 GIVEAWAY ✨", color=0xFFD700, timestamp=datetime.now())
        emb.add_field(name="🏆 Nagroda", value=f"```yaml\n{self.nagroda.value}```", inline=False)
        if self.opis.value: emb.add_field(name="📜 Zasady", value=f"> {self.opis.value}", inline=False)
        emb.set_footer(text="Kliknij ✨, aby dołączyć!")
        
        await interaction.response.send_message("🚀 Igrzyska rozpoczęte!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)
        
        await asyncio.sleep(seconds)
        winner = random.choice(view.participants) if view.participants else None
        
        if winner:
            res = discord.Embed(title="🎊 MAMY ZWYCIĘZCĘ! 🎊", color=THEME_COLOR, description=f"Los wskazał na {winner.mention}!\nNagroda: **{self.nagroda.value}**")
            await interaction.channel.send(content=f"🎉 Gratulacje {winner.mention}!", embed=res)
        else:
            await interaction.channel.send("😥 Igrzyska dobiegły końca, lecz nikt nie stanął w szranki.")
        await msg.edit(view=None)

# --- 🎫 WYROCZNIA POMOCY (TICKETY) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zakończ audiencję", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Komnata zostanie zamknięta za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz cel Twej wizyty...", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Gdy mechanizmy zawodzą"),
        discord.SelectOption(label="Skarbiec (Sklep)", emoji="💰", description="Wymiana złota na dobra"),
        discord.SelectOption(label="Skarga", emoji="⚖️", description="Gdy sprawiedliwość musi triumfować")
    ])
    async def callback(self, interaction, select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        emb = discord.Embed(title="🔮 Centrum Wsparcia 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", color=THEME_COLOR)
        emb.description = f"Witaj {interaction.user.mention}!\nStrażnicy zostali powiadomieni.\n\n> **Temat:** `{select.values[0]}`"
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto komnatę: {ch.mention}", ephemeral=True)

# --- 🛸 BRAMA WEJŚCIOWA (WERYFIKACJA) ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.primary, emoji="🛸", custom_id="v_b")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("🛸 Weryfikacja pomyślna. Witaj w 𝑺𝒘𝒊𝒓𝑯𝒖𝒃!", ephemeral=True)

# --- ⚔️ NARZĘDZIA MODERACJI ---
@bot.tree.command(name="clear", description="Oczyszcza czat z pyłu słów")
@app_commands.checks.has_permissions(manage_messages=True)
async def clr(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    emb = discord.Embed(description=f"🧹 Magiczna miotła usunęła **{ilosc}** wiadomości.", color=THEME_COLOR)
    await interaction.response.send_message(embed=emb, ephemeral=True)

# --- 👑 KOMENDY WŁADCY ---
@bot.tree.command(name="weryfikacja")
async def verif(interaction):
    emb = discord.Embed(title="🛸 BRAMA WERYFIKACJI", color=THEME_COLOR)
    emb.description = "Aby stać się pełnoprawnym mieszkańcem **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**, dotknij poniższego symbolu."
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Brama została postawiona.", ephemeral=True)

@bot.tree.command(name="ticket")
async def tick(interaction):
    emb = discord.Embed(title="📩 POTRZEBUJESZ POMOCY?", color=THEME_COLOR)
    emb.description = "Wybierz temat, a otworzymy dla Ciebie prywatną audiencję."
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("Wyrocznia jest gotowa.", ephemeral=True)

@bot.tree.command(name="konkurs")
async def conc(interaction): await interaction.response.send_modal(KonkursModal())

# --- 📜 KRONIKI WYDARZEŃ ---
@bot.event
async def on_member_join(member):
    await bot.update_status()
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="🪐 Nowa postać na orbicie!", color=THEME_COLOR)
        emb.description = f"Witaj {member.mention}! Niech gwiazdy Ci sprzyjają w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**."
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member): await bot.update_status()

@bot.event
async def on_ready():
    await bot.update_status()
    print(f"✅ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 AI zasiadło na tronie.")

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Artefakty zsynchronizowane.")

bot.run(os.getenv('DISCORD_TOKEN'))
