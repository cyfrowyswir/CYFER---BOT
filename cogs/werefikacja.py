import discord
from discord.ext import commands
from discord import app_commands

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Polski", style=discord.ButtonStyle.secondary, emoji="🇵🇱", custom_id="verify_pl")
    async def verify_pl(self, interaction: discord.Interaction, button: discord.ui.Button):
        ROLE_ID = 1451263520812568672
        role = interaction.guild.get_role(ROLE_ID)
        
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Pomyślnie zweryfikowano w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**! Przyznano rolę: **{role.name}**", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie odnaleziono roli weryfikacyjnej.", ephemeral=True)

    @discord.ui.button(label="English", style=discord.ButtonStyle.secondary, emoji="🇬🇧", custom_id="verify_en")
    async def verify_en(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Verification successful on **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**! Welcome.", ephemeral=True)

    @discord.ui.button(label="Połącz konto MC", style=discord.ButtonStyle.primary, emoji="🎁", custom_id="verify_mc")
    async def verify_mc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("ℹ️ Ta funkcja zostanie udostępniona wkrótce na **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!", ephemeral=True)

class Weryfikacja(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerificationView())

    @app_commands.command(name="setup-weryfikacja", description="Wysyła estetyczny panel weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_weryfikacja(self, interaction: discord.Interaction):
        BANNER_URL = "https://twoj-link.pl/weryfikacja_banner.png" 

        embed = discord.Embed(
            title="✨ Jak się zarejestrować? - How to register? ✨",
            description=(
                "**𝑺 𝑾 𝑰 𝑹 𝑯 𝑼 𝑩**\n\n"
                "🔑 Aby sie **zarejestrowac** kliknij ponizej na\n"
                "wybrany jezyk, życzymy mile spędzonego czasu\n"
                "na discordzie. Jesteśmy po to aby udoskonalić\n"
                "Twój projekt minecraft.\n\n"
                "🔑 To **register** click below on the language\n"
                "of your choice, using your nice time on discord.\n"
                "We are here to improve your minecraft project.\n\n"
                "💬 Jeżeli chcesz połączyć konto z **Oficjalnym\n"
                "serwerem 𝑺𝒘𝒊𝒓𝑯𝒖𝒃** wejdz na IP:\n"
                "`SwirHub.pl` i przepisz kod."
            ),
            color=discord.Color.from_rgb(255, 0, 255)
        )

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="© Copyright by 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 2022-2025", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)

        await interaction.response.send_message("✅ Panel weryfikacji został wysłany!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=VerificationView())

async def setup(bot: commands.Bot):
    await bot.add_cog(Weryfikacja(bot))
