import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button, Modal, TextInput

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- KONFIGURACJA POWITAŃ ---
ID_KANALU_POWITAN = 1234567890  # <--- TUTAJ WPISZ ID SWOJEGO KANAŁU

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(
            title="Witaj na serwerze!",
            description=f"Siemanko {member.mention}! Cieszymy się, że jesteś z nami na **{member.guild.name}**.\nZajrzyj na regulamin i baw się dobrze!",
            color=0x6c5ce7
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=f"Jesteś naszym {len(member.guild.members)} członkiem!")
        await channel.send(embed=emb)

# --- SYSTEM TICKETÓW (Slash) ---
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
            discord.SelectOption(label="Pomoc Ogólna", emoji="💎"),
            discord.SelectOption(label="Zamówienie - Bot", emoji="🤖"),
            discord.SelectOption(label="Zamówienie - Grafika", emoji="🎨"),
            discord.SelectOption(label="Odbiór Nagrody", emoji="🎁")
        ]
        super().__init__(placeholder="Wybierz kategorię...", options=options, custom_id="t_select")

    async def callback(self, interaction: discord.Interaction):
        ch_name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=ch_name, overwrites=overwrites)
        emb = discord.Embed(title=f"Zgłoszenie: {self.values[0]}", description=f"Witaj {interaction.user.mention}!\nOpisz swoją sprawę.", color=0x6c5ce7)
        await ch.send(content=interaction.user.mention, embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Utworzono: {ch.mention}", ephemeral=True)

# --- SLASH COMMANDS ---
@bot.tree.command(name="ticket_setup", description="Rozstawia panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    emb = discord.Embed(title="💎 DREAMCODE × TICKETY", description="Jeśli potrzebujesz pomocy lub masz pytania, wybierz **Pomoc ogólną**.\n\nW sprawie zamówień lub wyceny skorzystaj z odpowiedniej kategorii w menu.\nJeżeli jesteś kupującym, wysyłaj środki wyłącznie na dane podane przez bota.\n\nAdministracja prosi o niezakładanie zgłoszeń bez powodu.", color=0x6c5ce7)
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)
    await interaction.channel.send(embed=emb, view=View().add_item(TicketSelect()))

@bot.tree.command(name="ping", description="Sprawdza opóźnienie bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)}ms")

# --- KOMENDA DO SYNCHRONIZACJI (Wpisz !sync raz) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Komendy `/` zostały zsynchronizowane!")

@bot.event
async def on_ready():
    bot.add_view(View().add_item(TicketSelect()))
    bot.add_view(TicketControlView())
    print(f"Bot {bot.user} gotowy.")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
