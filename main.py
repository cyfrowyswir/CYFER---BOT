import discord
import os
from discord.ext import commands
from discord.ui import Select, View

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- WIDOK TICKETA (PO OTWARCIU) ---
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykanie kanału za 5 sekund...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await interaction.channel.delete()

# --- ROZWIJANE MENU Z KATEGORIAMI ---
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Pomoc Ogólna", description="Jeśli potrzebujesz wsparcia lub masz pytania.", emoji="💎"),
            discord.SelectOption(label="Odbiór Nagrody", description="Jeśli chcesz odebrać nagrodę.", emoji="🎁"),
            discord.SelectOption(label="Boty Discord", description="Jeśli chcesz zamówić bota.", emoji="🤖"),
            discord.SelectOption(label="Plugin", description="Jeśli chcesz zamówić plugin.", emoji="🔌"),
            discord.SelectOption(label="Grafika", description="Jeśli chcesz zamówić grafikę.", emoji="🎨"),
        ]
        super().__init__(placeholder="Wybierz jedną z opcji która Cię interesuje...", options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        # Tworzenie uprawnień dla nowego kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Nazwa kanału na podstawie wyboru
        category_name = self.values[0].lower().replace(" ", "-")
        channel = await guild.create_text_channel(f"ticket-{category_name}-{user.name}", overwrites=overwrites)
        
        # Wiadomość powitalna w tickecie
        embed = discord.Embed(
            title=f"Ticket: {self.values[0]}",
            description=f"Witaj {user.mention}! Zaraz ktoś z administracji Ci pomoże.\nOpisz swój problem poniżej.",
            color=0x9b59b6 # Fioletowy jak na screenie
        )
        
        await channel.send(embed=embed, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto ticket: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- KOMENDY ---
@bot.event
async def on_ready():
    print(f'✅ Bot ticketowy {bot.user} gotowy!')

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="💎 DREAMCODE × TICKETY",
        description=(
            "Jeżeli potrzebujesz pomocy, wsparcia lub masz pytania, skorzystaj z opcji **Pomoc Ogólna**.\n\n"
            "Jeżeli chcesz złożyć zamówienie bądź dowiedzieć się o przewidywanych kosztach skorzystaj z poprawnej kategorii w **poniższym menu**.\n\n"
            "Jeżeli jesteś **kupcem** pamiętaj, że pieniądze wysyłasz tylko na dane podane **przez bota**.\n\n"
            "~ Jako Administracja oraz Zespół prosimy o nie otwieranie zgłoszeń **dla zabawy** oraz o nie pingowanie nas, odpiszemy w wolnej chwili."
        ),
        color=0x9b59b6
    )
    # Tutaj możesz wstawić link do grafiki ze swojego screena
    embed.set_image(url="TU_WKLEJ_LINK_DO_OBRAZKA_Z_LOGO")
    embed.set_footer(text="© 2021 - 2025 • TwojaNazwa.pl")
    
    await ctx.send(embed=embed, view=TicketView())

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
