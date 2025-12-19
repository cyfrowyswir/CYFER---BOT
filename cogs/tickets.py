import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

ID_KANALU_LOGI = 1451263526848167956
ID_ROLI_ADMIN = 1451263520795529338

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="ticket_select",
        placeholder="Wybierz temat zgłoszenia...",
        options=[
            discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️"),
            discord.SelectOption(label="Sklep / Płatności", emoji="💳"),
            discord.SelectOption(label="Inna sprawa", emoji="📂")
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        # Logi
        log_channel = interaction.guild.get_channel(ID_KANALU_LOGI)
        if log_channel:
            emb = discord.Embed(title="📩 Nowy Ticket", description=f"Użytkownik: {interaction.user.mention}\nTemat: {select.values[0]}", color=discord.Color.green())
            await log_channel.send(embed=emb)

        await ch.send(f"{interaction.user.mention} | <@&{ID_ROLI_ADMIN}>", embed=discord.Embed(title="Wsparcie SwirHub", description="Opisz swój problem.", color=0x5865F2))
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Panel wsparcia")
    async def ticket(self, interaction: discord.Interaction):
        emb = discord.Embed(title="Centrum Pomocy", description="Wybierz temat z listy poniżej.", color=0x5865F2)
        await interaction.channel.send(embed=emb, view=TicketView())
        await interaction.response.send_message("Wysłano.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
