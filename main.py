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

# --- SYSTEM KONKURSU Z PRZYCISKIEM ---

def parse_duration(duration_str):
    time_dict = {"s": 1, "m": 60, "h": 3600}
    match = re.match(r"(\d+)([smh])", duration_str.lower())
    if match:
        amount, unit = match.groups()
        return int(amount) * time_dict[unit]
    return None

class GiveawayView(View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.participants = []

    @discord.ui.button(label="Dołącz 🎉", style=discord.ButtonStyle.blurple, custom_id="join_giveaway")
    async def join_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.participants:
            return await interaction.response.send_message("❌ Już bierzesz udział w tym konkursie!", ephemeral=True)
        
        self.participants.append(interaction.user)
        await interaction.response.send_message("✅ Pomyślnie dołączono do konkursu!", ephemeral=True)
        
        # Aktualizacja licznika w oryginalnym embedzie
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Uczestników: {len(self.participants)} | Powodzenia!")
        await interaction.message.edit(embed=embed)

class KonkursModal(Modal, title="Uruchom Konkurs 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    nagroda = TextInput(label="Nagroda", placeholder="Co jest do wygrania?", required=True)
    czas = TextInput(label="Czas trwania (np. 30s, 10m, 2h)", placeholder="Np. 15m", required=True)
    opis = TextInput(label="Zasady", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_duration(self.czas.value)
        if seconds is None:
            return await interaction.response.send_message("❌ Zły format czasu (użyj s, m, h)!", ephemeral=True)

        view = GiveawayView(timeout=seconds)
        emb = discord.Embed(
            title="🎉 NOWY KONKURS 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 🎉",
            description=f"**Nagroda:** {self.nagroda.value}\n\n**Zasady:** Kliknij przycisk poniżej!\n**Czas:** {self.czas.value}\n{f'**Info:** {self.opis.value}' if self.opis.value else ''}",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        emb.set_footer(text="Uczestników: 0 | Powodzenia!")
        
        await interaction.response.send_message("✅ Konkurs wystartował!", ephemeral=True)
        msg = await interaction.channel.send(content="@everyone", embed=emb, view=view)

        await asyncio.sleep(seconds)

        # Wyłączenie przycisku po czasie
        view.clear_items()
        view.stop()
        
        if len(view.participants) > 0:
            winner = random.choice(view.participants)
            end_emb = discord.Embed(
                title="🎊 WYNIKI KONKURSU 🎊",
                description=f"**Nagroda:** {self.nagroda.value}\n**Zwycięzca:** {winner.mention}\n**Liczba uczestników:** {len(view.participants)}",
                color=discord.Color.green()
            )
            await interaction.channel.send(content=f"Gratulacje {winner.mention}!", embed=end_emb)
            await msg.edit(content="🏁 **KONKURS ZAKOŃCZONY** 🏁", view=None)
        else:
            await interaction.channel.send(f"❌ Nikt nie dołączył do konkursu na **{self.nagroda.value}**.")
            await msg.edit(content="🏁 **KONKURS ZAKOŃCZONY (Brak uczestników)** 🏁", view=None)

# --- POZOSTAŁE KOMENDY MODERACYJNE I SYSTEMY ---

@bot.tree.command(name="konkurs")
@app_commands.checks.has_permissions(administrator=True)
async def konkurs(interaction): await interaction.response.send_modal(KonkursModal())

@bot.tree.command(name="tekst")
@app_commands.checks.has_permissions(administrator=True)
async def tekst(interaction): await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="clear")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(f"✅ Usunięto {ilosc} wiadomości.", ephemeral=True)

@bot.tree.command(name="weryfikacja")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction):
    await interaction.channel.send(embed=discord.Embed(title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja", description="Kliknij przycisk poniżej!", color=THEME_COLOR), view=VerifyView())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

@bot.tree.command(name="ticket")
@app_commands.checks.has_permissions(administrator=True)
async def t_setup(interaction):
    await interaction.channel.send(embed=discord.Embed(title="💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × TICKETY", description="Wybierz kategorię.", color=THEME_COLOR), view=TicketLauncher())
    await interaction.response.send_message("Wysłano!", ephemeral=True)

# --- KLASY DLA TICKETÓW I WERYFIKACJI ---

class TekstModal(Modal, title="Embed 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    t = TextInput(label="Tytuł"); o = TextInput(label="Opis", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction):
        await interaction.channel.send(embed=discord.Embed(title=self.t.value, description=self.o.value, color=THEME_COLOR))
        await interaction.response.send_message("✅", ephemeral=True)

class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Weryfikacja", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Zweryfikowano!", ephemeral=True)

class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Usuwanie kanału..."); await asyncio.sleep(5); await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz kategorię...", options=[
        discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
        discord.SelectOption(label="Zamówienie-MC", emoji="⛏️"),
        discord.SelectOption(label="Zamówienie-STUDIO", emoji="🎨")
    ])
    async def callback(self, interaction, select):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=discord.Embed(title=f"Kategoria: {select.values[0]}", color=THEME_COLOR), view=TicketControlView())
        await interaction.response.send_message(f"✅ {ch.mention}", ephemeral=True)

# --- URUCHOMIENIE ---
@bot.command()
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send("✅ Zsynchronizowano komendy dla **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="𝑺𝒘𝒊𝒓𝑯𝒖𝒃"))
    print(f"✅ Zalogowano jako {bot.user}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
