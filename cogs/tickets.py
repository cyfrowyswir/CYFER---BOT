import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="swirhub_ticket_v5",
        placeholder="🌐 Wybierz rodzaj zgłoszenia...",
        options=[
            discord.SelectOption(
                label="Pomoc Techniczna", 
                description="Problemy z serwerem, błędy, bugi.",
                emoji="🛠️", 
                value="pomoc"
            ),
            discord.SelectOption(
                label="Sklep i Płatności", 
                description="Pytania o rangi, problemy z zakupem.",
                emoji="💰", 
                value="sklep"
            ),
            discord.SelectOption(
                label="Skarga / Odwołanie", 
                description="Zgłoś gracza lub odwołaj się od kary.",
                emoji="⚖️", 
                value="skarga"
            )
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: Select):
        # Ustawienia kanału (tylko dla usera i adminów)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Tworzenie kanału z ładną nazwą
        ch = await interaction.guild.create_text_channel(
            name=f"🆘-{interaction.user.name}", 
            overwrites=overwrites,
            category=interaction.channel.category # Tworzy ticket w tej samej kategorii co panel
        )
        
        # Logowanie do kanału logów (ID: 1451263526848167956)
        log_chan = interaction.guild.get_channel(1451263526848167956)
        if log_chan:
            log_emb = discord.Embed(title="📩 Nowy Ticket", color=0x2ecc71)
            log_emb.add_field(name="Użytkownik", value=interaction.user.mention, inline=True)
            log_emb.add_field(name="Temat", value=select.values[0].capitalize(), inline=True)
            log_emb.add_field(name="Kanał", value=ch.mention, inline=False)
            await log_chan.send(embed=log_emb)

        # Powitanie w tickecie
        welcome_emb = discord.Embed(
            title="✨ Zgłoszenie Przyjęte",
            description=f"Witaj {interaction.user.mention}!\n\nOpisz dokładnie swój problem, a administracja zajmie się nim najszybciej jak to możliwe.\n\n**Temat:** {select.values[0].capitalize()}",
            color=0x5865F2
        )
        welcome_emb.set_footer(text="SwirHub Support System")
        
        await ch.send(embed=welcome_emb)
        await interaction.response.send_message(f"✅ Twój ticket został otwarty: {ch.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Wysyła profesjonalny panel zgłoszeń")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="📩 Centrum Wsparcia 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=(
                "Potrzebujesz pomocy? Masz problem z płatnością?\n"
                "Wybierz odpowiednią kategorię z menu poniżej!\n\n"
                "**⌛ Czas odpowiedzi:** Zazwyczaj do 24h\n"
                "**⚠️ Uwaga:** Nie spamuj bez potrzeby."
            ),
            color=0x5865F2
        )
        emb.set_image(url="https://i.imgur.com/uVf3KUn.png") # Możesz tu wstawić link do swojego loga/grafiki
        emb.set_footer(text="System obsługi zgłoszeń v2.0")
        
        await interaction.channel.send(embed=emb, view=TicketView())
        await interaction.response.send_message("Panel pomocy został wysłany!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
