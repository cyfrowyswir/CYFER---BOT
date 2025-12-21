import discord
from discord import app_commands
from discord.ext import commands

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # To sprawia, że przycisk nie wygasa

    @discord.ui.button(
        label="Kliknij tutaj, aby się zweryfikować", 
        style=discord.ButtonStyle.success, 
        custom_id="swirhub_ver_v11", # Nowe ID, żeby odświeżyć system
        emoji="✅"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1451263520812568672 # Twoje ID roli
        role = interaction.guild.get_role(role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Błąd: Nie znaleziono roli weryfikacji!", ephemeral=True)

        try:
            # Sprawdzamy czy użytkownik ma już rolę
            if role in interaction.user.roles:
                await interaction.response.send_message("Jesteś już zweryfikowany! 🛡️", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Pomyślnie nadano dostęp do serwera! Witaj w społeczności.", ephemeral=True)
                
                # Opcjonalny log weryfikacji
                log_chan = interaction.guild.get_channel(1451263526848167956)
                if log_chan:
                    await log_chan.send(f"👤 {interaction.user.mention} przeszedł weryfikację.")

        except discord.Forbidden:
            # Ten błąd wyskoczy, gdy ranga bota będzie ZA NISKO w ustawieniach serwera
            await interaction.response.send_message("❌ Błąd uprawnień! Upewnij się, że ranga bota jest wyżej niż ranga użytkownika w ustawieniach serwera.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

class Weryfikacja(commands.Cog):
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
            color=0x2ecc71
        )
        # Dodaje miniaturkę (avatar bota lub serwera)
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        emb.set_footer(text="Bezpieczeństwo serwera zapewnia SwirHub Bot")
        
        # Wysyłamy wiadomość z naszym "ładnym" widokiem (przyciskiem)
        await interaction.channel.send(embed=emb, view=VerificationView())
        await interaction.response.send_message("✅ Panel weryfikacji wysłany!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weryfikacja(bot))
