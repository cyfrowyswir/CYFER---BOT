import discord
from discord import app_commands
from discord.ext import commands

class VerificationView(discord.ui.View):
    def __init__(self):
        # Stały czas trwania, aby przycisk nigdy nie wygasł
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Kliknij tutaj, aby się zweryfikować", 
        style=discord.ButtonStyle.success, 
        custom_id="swirhub_ver_permanent_v1", # Unikalne ID dla bazy bota
        emoji="✅"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1451263520812568672 # Twoje ID roli
        role = interaction.guild.get_role(role_id)
        
        if not role:
            return await interaction.response.send_message("❌ Błąd: Nie odnaleziono roli weryfikacji.", ephemeral=True)

        try:
            if role in interaction.user.roles:
                await interaction.response.send_message("🛡️ Jesteś już zweryfikowanym członkiem **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✨ **Sukces!** Twoja weryfikacja przebiegła pomyślnie. Witaj na pokładzie!", ephemeral=True)
                
                # Opcjonalny log na kanał logów
                log_chan = interaction.guild.get_channel(1451263526848167956)
                if log_chan:
                    await log_chan.send(f"✅ Użytkownik {interaction.user.mention} pomyślnie przeszedł weryfikację.")

        except discord.Forbidden:
            await interaction.response.send_message("❌ **Błąd uprawnień!** Moja ranga jest zbyt nisko, by nadać Ci rolę. Poinformuj administratora.", ephemeral=True)

class Weryfikacja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="weryfikacja", description="Wysyła estetyczny panel weryfikacji serwera")
    @app_commands.checks.has_permissions(administrator=True)
    async def weryfikacja(self, interaction: discord.Interaction):
        # Powrót do pięknego designu z obrazka
        emb = discord.Embed(
            title="🛡️ System Weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=(
                "**Witamy na naszym serwerze!**\n\n"
                "Aby uzyskać dostęp do reszty kanałów i funkcji, musisz "
                "zaakceptować nasz regulamin i kliknąć przycisk poniżej.\n\n"
                "**Zasady w skrócie:**\n"
                "• Szanuj innych użytkowników. 🤝\n"
                "• Zakaz reklamowania innych serwerów. 🚫\n"
                "• Baw się dobrze! 🎉\n\n"
                "*Bezpieczeństwo serwera zapewnia SwirHub Bot*"
            ),
            color=0x2ecc71
        )
        
        # Dodanie Twojej ikony (tej z czarnym kotem na screenie)
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        emb.set_footer(text="System Weryfikacji • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # Wysłanie panelu z przyciskiem
        await interaction.channel.send(embed=emb, view=VerificationView())
        await interaction.response.send_message("✅ Piękny panel weryfikacji został wysłany!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weryfikacja(bot))
