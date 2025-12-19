import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tekst", description="Wysyła ogłoszenie w ramce")
    async def tekst(self, interaction: discord.Interaction, tytul: str, tresc: str):
        emb = discord.Embed(title=tytul, description=tresc, color=0x5865F2)
        emb.set_footer(text=f"SwirHub - {interaction.user.name}")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie wysłane.", ephemeral=True)

    @app_commands.command(name="clear", description="Usuwa określoną liczbę wiadomości")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        await interaction.channel.purge(limit=ilosc)
        await interaction.response.send_message(f"🧹 Usunięto {ilosc} wiadomości.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
