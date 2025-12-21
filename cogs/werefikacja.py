import discord
from discord import app_commands
from discord.ext import commands

class VerificationView(discord.ui.View):
    def __init__(self):
        # Timeout=None jest kluczowy, by przyciski nie wygasły
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Kliknij tutaj, aby się zweryfikować", 
        style=discord.ButtonStyle.success, 
        custom_id="swirhub_ver_fixed", # To ID musi być zawsze takie samo!
        emoji="✅"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1451263520812568672
        role = interaction.guild.get_role(role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Błąd roli!", ephemeral=True)

        try:
            if role in interaction.user.roles:
                await interaction.response.send_message("Już masz weryfikację! 🛡️", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Witaj na serwerze!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot ma za niską rangę!", ephemeral=True)

class Weryfikacja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="weryfikacja", description="Wysyła stały panel weryfikacji")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="🛡️ System Weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description="Kliknij przycisk poniżej, aby uzyskać dostęp!",
            color=0x2ecc71
        )
        # Rejestrujemy widok przy wysyłaniu
        await interaction.channel.send(embed=emb, view=VerificationView())
        await interaction.response.send_message("Wysłano!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weryfikacja(bot))
