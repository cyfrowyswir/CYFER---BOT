import discord
from discord.ext import commands
from discord import app_commands

# --- MODAL: OKNO WPISYWANIA TREŚCI OGŁOSZENIA ---
class OgloszenieModal(discord.ui.Modal, title="Kreator Ogłoszenia 𝑺𝒘𝒊𝒓𝑯𝒖𝒃"):
    tytul = discord.ui.TextInput(
        label="Tytuł Ogłoszenia",
        placeholder="Np. Przerwa techniczna, Nowa aktualizacja...",
        required=True,
        style=discord.TextStyle.short # Poprawione tutaj
    )
    
    naglowek = discord.ui.TextInput(
        label="Nagłówek (Główny tekst pod tytułem)",
        placeholder="Np. WAŻNE INFORMACJE DLA GRACZY",
        required=False,
        default="Ｓ Ｗ Ｉ Ｒ Ｈ Ｕ Ｂ"
    )

    tresc = discord.ui.TextInput(
        label="Treść wiadomości",
        placeholder="Tutaj wpisz całą treść swojego ogłoszenia...",
        style=discord.TextStyle.long, # Tutaj też musi być TextStyle.long
        required=True,
        min_length=10
    )

    obrazek = discord.ui.TextInput(
        label="Link do obrazka (opcjonalnie)",
        placeholder="https://link-do-zdjecia.pl/obrazek.png",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Tworzenie estetycznego Embedu na wzór powitania
        embed = discord.Embed(
            title=f"📢 {self.tytul.value}",
            description=f"**{self.naglowek.value}**\n\n{self.tresc.value}",
            color=discord.Color.from_rgb(255, 0, 255) # Spójny różowy kolor
        )

        if self.obrazek.value.startswith("http"):
            embed.set_image(url=self.obrazek.value)

        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        embed.set_footer(
            text=f"Ogłoszenie wysłane przez: {interaction.user.display_name} • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Ogłoszenie zostało wysłane pomyślnie!", ephemeral=True)

class Ogloszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ogloszenie", description="Wysyła estetyczny panel ogłoszenia Serwera 𝑺𝒘𝒊𝒓𝑯𝒖𝒃")
    @app_commands.checks.has_permissions(administrator=True)
    async def ogloszenie(self, interaction: discord.Interaction):
        await interaction.response.send_modal(OgloszenieModal())

async def setup(bot):
    await bot.add_cog(Ogloszenia(bot))
