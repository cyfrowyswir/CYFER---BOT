import discord
from discord import app_commands, ui
from discord.ext import commands

# Okienko GUI do wpisywania treści ogłoszenia
class OgloszenieModal(ui.Modal, title="Tworzenie Ogłoszenia 📢"):
    tytul = ui.TextInput(label="Tytuł", placeholder="np. REGULAMIN SERWERA", min_length=2)
    tresc = ui.TextInput(
        label="Treść punktów (każdy w nowej linii)", 
        style=discord.TextStyle.paragraph, 
        placeholder="Punkt pierwszy\nPunkt drugi\nPunkt trzeci...",
        min_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Rozdzielamy tekst na linie i dodajemy numerki §
        linie = self.tresc.value.split('\n')
        sformatowany_tekst = ""
        
        for i, linia in enumerate(linie, 1):
            if linia.strip(): # Pomijamy puste linie
                # Formatowanie: §0.01 Treść punktu
                numer = f"§0.{i:02d}" 
                sformatowany_tekst += f"**{numer}** {linia.strip()}\n"

        emb = discord.Embed(
            title=f"📢 {self.tytul.value}",
            description=sformatowany_tekst,
            color=0x5865F2
        )
        
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)
        
        emb.set_footer(
            text=f"Ogłoszenie od: {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        emb.timestamp = discord.utils.utcnow()

        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Ogłoszenie sformatowane i wysłane!", ephemeral=True)

class Ogloszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tekst", description="Otwiera GUI do tworzenia sformatowanego tekstu")
    @app_commands.checks.has_permissions(administrator=True)
    async def tekst(self, interaction: discord.Interaction):
        # Wywołanie okna Modal zamiast zwykłej komendy tekstowej
        await interaction.response.send_modal(OgloszenieModal())

async def setup(bot):
    await bot.add_cog(Ogloszenia(bot))
