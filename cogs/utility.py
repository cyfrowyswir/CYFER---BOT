import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- KOMENDA /TEKST ---
    @app_commands.command(name="tekst", description="Tworzy estetyczne ogłoszenie")
    async def tekst(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TekstModal())

    # --- KOMENDA /WERYFIKACJA ---
    @app_commands.command(name="weryfikacja", description="Panel weryfikacji użytkowników")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Weryfikacja",
            description="Kliknij przycisk poniżej, aby otrzymać rangę i uzyskać dostęp do serwera.",
            color=0x5865F2
        )
        view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(label="Odbierz dostęp", style=discord.ButtonStyle.primary, custom_id="verify_button_v1")
        
        async def v_callback(it: discord.Interaction):
            role = it.guild.get_role(1451263520812568672) # Twoje ID roli weryfikacyjnej
            if role:
                await it.user.add_roles(role)
                await it.response.send_message("✅ Pomyślnie nadano rangę!", ephemeral=True)
        
        btn.callback = v_callback
        view.add_item(btn)
        await interaction.channel.send(embed=emb, view=view)
        await interaction.response.send_message("Panel weryfikacji został wysłany.", ephemeral=True)

    # --- KOMENDA /CLEAR ---
    @app_commands.command(name="clear", description="Oczyszcza czat z wiadomości")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        await interaction.channel.purge(limit=ilosc)
        await interaction.response.send_message(f"🧹 Usunięto **{ilosc}** wiadomości.", ephemeral=True)

class TekstModal(Modal, title="🖋️ Redagowanie Ogłoszenia"):
    tytul = TextInput(label="Tytuł", placeholder="Nagłówek ogłoszenia...", required=True)
    tresc = TextInput(label="Treść", style=discord.TextStyle.paragraph, placeholder="Co chcesz przekazać?", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.tytul.value, description=self.tresc.value, color=0x5865F2)
        emb.set_footer(text=f"Nadawca: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie opublikowane.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
