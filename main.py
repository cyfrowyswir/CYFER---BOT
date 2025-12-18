import discord
import os
import asyncio
from discord.ext import commands
from discord.ui import Select, View, Button, Modal, TextInput

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- SYSTEM TICKETÓW ---
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

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
        if discord.utils.get(interaction.guild.text_channels, name=ch_name):
            return await interaction.response.send_message("❌ Masz już otwarty ticket!", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=ch_name, overwrites=overwrites)
        emb = discord.Embed(title=f"Zgłoszenie: {self.values[0]}", description=f"Witaj {interaction.user.mention}!\nOpisz swoją sprawę.", color=0x6c5ce7)
        await ch.send(content=interaction.user.mention, embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Utworzono: {ch.mention}", ephemeral=True)

# --- SYSTEM REGULAMINU (GUI) ---
class RegModal(Modal, title="Tworzenie Regulaminu"):
    t = TextInput(label="Tytuł", required=True)
    o = TextInput(label="Treść", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.t.value, description=self.o.value, color=0x6c5ce7)
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("Wysłano!", ephemeral=True)

class RegView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📝 Stwórz Regulamin", style=discord.ButtonStyle.primary)
    async def open_m(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RegModal())

# --- KOMENDY ---
@bot.event
async def on_ready():
    bot.add_view(View().add_item(TicketSelect()))
    bot.add_view(TicketControlView())
    bot.add_view(RegView())
    print(f"Bot {bot.user} gotowy.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    await ctx.message.delete()
    emb = discord.Embed(title="💎 DREAMCODE × TICKETY", description="Jeśli potrzebujesz pomocy lub masz pytania, wybierz **Pomoc ogólną**.\n\nW sprawie zamówień lub wyceny skorzystaj z odpowiedniej kategorii w menu.\nJeżeli jesteś kupującym, wysyłaj środki wyłącznie na dane podane przez bota.\n\nAdministracja oraz Zespół proszą o niezakładanie zgłoszeń bez powodu i niepingowanie — odpowiemy, gdy tylko będziemy dostępni.", color=0x6c5ce7)
    await ctx.send(embed=emb, view=View().add_item(TicketSelect()))

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.message.delete()
    await ctx.send(view=RegView())

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
