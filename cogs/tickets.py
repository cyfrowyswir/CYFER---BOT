import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="ticket_v3",
        placeholder="Wybierz temat zgłoszenia...",
        options=[
            discord.SelectOption(label="Pomoc", emoji="🛠️"),
            discord.SelectOption(label="Sklep", emoji="💰")
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"Witaj {interaction.user.mention}, opisz sprawę.")
        await interaction.response.send_message(f"Otwarto ticket: {ch.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Panel zgłoszeń")
    async def ticket(self, interaction: discord.Interaction):
        await interaction.channel.send(embed=discord.Embed(title="Pomoc", description="Wybierz temat poniżej.", color=0x5865F2), view=TicketView())
        await interaction.response.send_message("Wysłano.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
