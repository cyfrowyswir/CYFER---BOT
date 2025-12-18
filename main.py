import discord
import os
import asyncio
from discord.ext import commands
from discord.ui import Select, View, Button

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

THEME_COLOR = 0x6c5ce7 

# --- 1. PANEL ZARZĄDZANIA W ŚRODKU TICKETA ---
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="🔒 Zamykanie...",
            description=f"Ticket zostanie usunięty za **5 sekund**.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 2. MENU WYBORU KATEGORII ---
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Pomoc Ogólna", description="Pytania i wsparcie ogólne.", emoji="💎"),
            discord.SelectOption(label="Zamówienie - Bot", description="Chcesz zamówić bota?", emoji="🤖"),
            discord.SelectOption(label="Zamówienie - Grafika", description="Potrzebujesz grafiki?", emoji="🎨"),
            discord.SelectOption(label="Odbiór Nagrody", description="Odbiór wygranych.", emoji="🎁"),
        ]
        super().__init__(
            placeholder="Wybierz jedną z opcji która Cię interesuje...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category_name = self.values[0]
        channel_name = f"ticket-{interaction.user.name.lower()}"

        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"❌ Masz już otwarty ticket: {existing_channel.mention}!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        try:
            ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
            
            embed = discord.Embed(
                title=f"Zgłoszenie: {category_name}",
                description=(
                    f"Witaj {interaction.user.mention}!\n\n"
                    "Dziękujemy za kontakt. Opisz dokładnie swój problem lub sprawę.\n"
                    "**Administracja odpowie najszybciej jak to możliwe.**"
                ),
                color=THEME_COLOR
            )
            embed.set_footer(text="Użyj przycisku poniżej, aby zamknąć ten kanał.")

            await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketControlView())
            await interaction.response.send_message(f"✅ Utworzono ticket: {ticket_channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- 3. START I KOMENDY ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} online!')
    bot.add_view(TicketLauncher())
    bot.add_view(TicketControlView())

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    await ctx.message.delete()
    
    # --- NOWY OPIS ZGODNY Z TWOJĄ PROŚBĄ ---
    embed = discord.Embed(
        title="💎 DREAMCODE × TICKETY",
        description=(
            "Jeśli potrzebujesz pomocy lub masz pytania, wybierz **Pomoc ogólną**.\n\n"
            "W sprawie zamówień lub wyceny skorzystaj z odpowiedniej kategorii w menu.\n"
            "Jeżeli jesteś kupującym, wysyłaj środki wyłącznie na dane podane przez bota.\n\n"
            "Administracja oraz Zespół proszą o niezakładanie zgłoszeń bez powodu i niepingowanie — odpowiemy, gdy tylko będziemy dostępni."
        ),
        color=THEME_COLOR
    )
    # Miniatura (logo) i obrazek zostały usunięte
    embed.set_footer(text="DreamCode • System zgłoszeń")

    await ctx.send(embed=embed, view=TicketLauncher())

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
