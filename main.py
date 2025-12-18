import discord
import os
from discord.ext import commands
from discord.ui import Select, View

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True # TO JEST KLUCZOWE
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- PANEL TICKETA (Po otwarciu) ---
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Zamykam ticket za 5 sekund...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await interaction.channel.delete()

# --- ROZWIJANE MENU (Select Menu) ---
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Pomoc Ogólna", description="Pytania i wsparcie.", emoji="💎"),
            discord.SelectOption(label="Odbiór Nagrody", description="Odbiór wygranej.", emoji="🎁"),
            discord.SelectOption(label="Boty Discord", description="Zamówienie bota.", emoji="🤖"),
            discord.SelectOption(label="Pluginy", description="Zamówienie pluginu.", emoji="🔌"),
            discord.SelectOption(label="Grafika", description="Zamówienie grafiki.", emoji="🎨"),
        ]
        super().__init__(placeholder="Wybierz temat zgłoszenia...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Tutaj dzieje się magia po wybraniu opcji
        guild = interaction.guild
        category_name = self.values[0] # Np. "Grafika"
        
        # Tworzymy nazwę kanału (np. ticket-grafika-nick)
        channel_name = f"ticket-{category_name.lower().replace(' ', '-')}-{interaction.user.name}"
        
        # Uprawnienia: Tylko Admin, Bot i Użytkownik widzą kanał
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Tworzenie kanału
        try:
            channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
            
            # Wiadomość w środku nowego kanału
            embed = discord.Embed(
                title=f"Nowe zgłoszenie: {category_name}",
                description=f"Witaj {interaction.user.mention}!\nOpisz dokładnie swój problem. Administracja zaraz odpisze.",
                color=0x9b59b6
            )
            await channel.send(embed=embed, view=TicketControlView())
            
            # Informacja zwrotna (tylko dla klikającego)
            await interaction.response.send_message(f"✅ Utworzono ticket: {channel.mention}", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd przy tworzeniu kanału: {e}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- START I KOMENDY ---
@bot.event
async def on_ready():
    print(f'✅ ZALOGOWANO JAKO: {bot.user}')
    print('✅ Czekam na komendy...')

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    # Próbujemy usunąć Twoją wiadomość, ale jak się nie uda, to trudno - idziemy dalej
    try:
        await ctx.message.delete()
    except:
        pass 

    embed = discord.Embed(
        title="💎 DREAMCODE × TICKETY",
        description=(
            "Jeżeli potrzebujesz pomocy, wsparcia lub masz pytania, skorzystaj z opcji **Pomoc Ogólna**.\n\n"
            "Jeżeli chcesz złożyć zamówienie, wybierz odpowiednią kategorię w **menu poniżej**.\n\n"
            "⚠️ Nie otwieraj ticketów dla zabawy!"
        ),
        color=0x9b59b6
    )
    # Pamiętaj, żeby tu wkleić swój link do obrazka
    # embed.set_image(url="LINK_DO_OBRAZKA")
    
    await ctx.send(embed=embed, view=TicketView())

# --- DIAGNOSTYKA BŁĘDÓW ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Nie masz uprawnień Administratora!")
    elif isinstance(error, commands.CommandNotFound):
        # Bot ignoruje błędne komendy, żeby nie spamować
        pass
    else:
        print(f"BŁĄD: {error}") # Zobaczysz to w logach Koyeb

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ Nie znaleziono tokena!")
