import discord
from discord import app_commands
from discord.ext import commands

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Kliknij tutaj, aby się zweryfikować", 
        style=discord.ButtonStyle.success, 
        custom_id="swirhub_ver_v10", # Zmienione ID, żeby odświeżyć przycisk
        emoji="✅"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1451263520812568672
        role = interaction.guild.get_role(role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Nie znaleziono roli o podanym ID!", ephemeral=True)

        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Pomyślnie zweryfikowano!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot nie ma uprawnień (Zarządzanie Rolami) lub jego ranga jest za nisko w liście ról!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

class Weryfikacja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="weryfikacja", description="Wysyła panel weryfikacji")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="🛡️ Weryfikacja SwirHub",
            description="Kliknij przycisk poniżej, aby otrzymać dostęp do serwera!",
            color=0x2ecc71
        )
        await interaction.channel.send(embed=emb, view=VerificationView())
        await interaction.response.send_message("Wysłano panel!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weryfikacja(bot))
