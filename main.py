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

# Kolor przewodni (Fioletowy)
THEME_COLOR = 0x6c5ce7 

# --- 1. PANEL ZARZĄDZANIA W ŚRODKU TICKETA ---
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij Zgłoszenie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Efekt wizualny zamykania
        embed = discord.Embed(
            title="🔒 Zamykanie...",
            description=f"Ticket zostanie usunięty za **5 sekund** przez {interaction.user.mention}.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        
        # Czekamy 5 sekund i usuwamy kanał
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 2. MENU WYBORU KATEGORII (DROPDOWN) ---
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Pomoc Ogólna", 
                description="Masz problem lub pytanie? Kliknij tutaj.", 
                emoji="💎"
            ),
            discord.SelectOption(
                label="Zamówienie - Bot", 
                description="Chcesz zamówić własnego bota Discord?", 
                emoji="🤖"
            ),
            discord.SelectOption(
                label="Zamówienie - Grafika", 
                description="Potrzebujesz banneru, logo lub avatara?", 
                emoji="🎨"
            ),
            discord.SelectOption(
                label="Odbiór Nagrody", 
                description="Wygrałeś w konkursie? Odbierz nagrodę!", 
                emoji="🎁"
            ),
            discord.SelectOption(
                label="Współpraca", 
                description="Chcesz nawiązać partnerstwo?", 
                emoji="🤝"
            ),
        ]
        super().__init__(
            placeholder="Wybierz kategorię zgłoszenia...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        # Sprawdzamy, czy użytkownik nie ma już otwartego ticketa w tej kategorii
        guild = interaction.guild
        category_name = self.values[0]
        channel_name = f"ticket-{interaction.user.name.lower()}"

        # Szukamy czy kanał już istnieje
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"❌ Masz już otwarty ticket: {existing_channel.mention}!", ephemeral=True)
            return

        # Uprawnienia: Tylko Admin, Bot i User widzą kanał
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Tworzenie kanału
        try:
            ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
            
            # --- Wygląd wiadomości WEWNĄTRZ ticketa ---
            embed = discord.Embed(
                title=f"{category_name}",
                description=(
                    f"Witaj {interaction.user.mention}!\n\n"
                    "Dziękujemy za kontakt. Opisz dokładnie swój problem lub zamówienie.\n"
                    "**Administracja odpowie najszybciej jak to możliwe.**\n\n"
                    "⛔ *Prosimy o cierpliwość i nie pingowanie bez potrzeby.*"
                ),
                color=THEME_COLOR
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text="Aby zamknąć zgłoszenie, kliknij przycisk poniżej.")

            await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketControlView())
            
            # Potwierdzenie dla klikającego (znika samo)
            await interaction.response.send_message(f"✅ Twój ticket został utworzony: {ticket_channel.mention}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

# --- 3. GŁÓWNY WIDOK (View) ---
class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- 4. START BOTA I KOMENDY ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} jest gotowy i nasłuchuje!')
    # To sprawia, że przyciski działają nawet po restarcie bota (Persistence)
    bot.add_view(TicketLauncher())
    bot.add_view(TicketControlView())

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    await ctx.message.delete()
    
    # --- Wygląd GŁÓWNEGO PANELU ---
    embed = discord.Embed(
        title="📬 CENTRUM POMOCY",
        description=(
            "> **Witaj w naszym systemie zgłoszeń!**\n\n"
            "Wybierz z menu poniżej odpowiednią kategorię, aby skontaktować się z administracją.\n\n"
            "🛡️ **Pomoc Ogólna** - Problemy techniczne i pytania\n"
            "💰 **Zamówienia** - Boty, strony www, grafika\n"
            "🎁 **Nagrody** - Odbiór wygranych konkursowych\n"
        ),
        color=THEME_COLOR
    )
    
    # Jeśli serwer ma ikonę, ustawiamy ją jako miniaturkę
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    
    embed.set_image(url="https://imgur.com/a/RmMR1U0") # Możesz tu wstawić swój baner!
    embed.set_footer(text="WizardStudio System • Bezpieczne Zgłoszenia")

    await ctx.send(embed=embed, view=TicketLauncher())

token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
