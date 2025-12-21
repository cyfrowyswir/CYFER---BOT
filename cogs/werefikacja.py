import discord
from discord import app_commands
from discord.ext import commands

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Przycisk nie wygaśnie po restarcie

    @discord.ui.button(
        label="Kliknij tutaj, aby się zweryfikować", 
        style=discord.ButtonStyle.success, 
        custom_id="swirhub_ver_v5",
        emoji="✅"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1451263520812568672 # Twoje ID roli
        role = interaction.guild.get_role(role_id)
        
        if role in interaction.user.roles:
            await interaction.response.send_message("Jesteś już zweryfikowany! 🛡️", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Pomyślnie nadano dostęp do serwera! Witaj w społeczności.", ephemeral=True)
                
                # Opcjonalnie: log weryfikacji
                log_chan = interaction.guild.get_channel(1451263526848167956)
                if log_chan:
                    await log_chan.send(f"👤 {interaction.user.mention} przeszedł weryfikację.")
            except Exception as e:
                await interaction.response.send_message(f"❌ Wystąpił błąd z rangą: {e}", ephemeral=True)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="weryfikacja", description="Wysyła estetyczny panel weryfikacji")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="🛡️ System Weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=(
                "Witamy na naszym serwerze!\n\n"
                "Aby uzyskać dostęp do reszty kanałów i funkcji, "
                "musisz zaakceptować nasz regulamin i kliknąć przycisk poniżej.\n\n"
                "**Zasady w skrócie:**\n"
                "• Szanuj innych użytkowników.\n"
                "• Zakaz reklamowania innych serwerów.\n"
                "• Baw się dobrze! 🎉"
            ),
            color=0x2ecc71 # Zielony kolor weryfikacji
        )
        emb.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        emb.set_footer(text="Bezpieczeństwo serwera zapewnia SwirHub Bot")
        
        await interaction.channel.send(embed=emb, view=VerificationView())
        await interaction.response.send_message("✅ Panel weryfikacji wysłany!", ephemeral=True)

    @app_commands.command(name="tekst", description="Wysyła ogłoszenie")
    async def tekst(self, interaction: discord.Interaction, tytul: str, tresc: str):
        emb = discord.Embed(title=tytul, description=tresc, color=0x5865F2)
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("Wysłano.", ephemeral=True)

    @app_commands.command(name="clear", description="Usuwa wiadomości")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, ilosc: int):
        await interaction.channel.purge(limit=ilosc)
        await interaction.response.send_message(f"Usunięto {ilosc} wiadomości.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
