import discord
from discord.ext import commands
from discord import app_commands
import datetime

# --- SYSTEM WERYFIKACJI 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
# Moduł: System Zgłoszeń (Tickets)
# Status: Pełna wersja funkcjonalna

class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Otwórz Ticket", 
        style=discord.ButtonStyle.primary, 
        custom_id="create_ticket_btn",
        emoji="📩"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Szukanie kategorii dla ticketów
        category = discord.utils.get(guild.categories, name="TICKETY")
        
        if not category:
            await interaction.response.send_message(
                "❌ Błąd: Nie znaleziono kategorii `TICKETY`. Powiadom administratora!", 
                ephemeral=True
            )
            return

        # Sprawdzenie czy użytkownik nie ma już otwartego ticketa
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(
                f"⚠️ Masz już otwarty ticket: {existing_channel.mention}", 
                ephemeral=True
            )
            return

        # Ustawienia uprawnień dla kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        # Tworzenie kanału
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            reason=f"Ticket utworzony przez {user}"
        )

        await interaction.response.send_message(f"✅ Twój ticket został utworzony: {channel.mention}", ephemeral=True)

        # Wiadomość powitalna w tickecie
        embed = discord.Embed(
            title="📩 Nowe Zgłoszenie | 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=(
                f"Witaj {user.mention}!\n\n"
                "Opisz swój problem lub powód otwarcia zgłoszenia.\n"
                "Moderacja odezwie się do Ciebie tak szybko, jak to możliwe.\n\n"
                "**Zasady:**\n"
                "• Nie oznaczaj administracji bez potrzeby.\n"
                "• Zachowaj kulturę wypowiedzi."
            ),
            color=0x2b2d31,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="System Weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", icon_url=user.display_avatar.url)
        
        await channel.send(embed=embed, view=TicketControlView())

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔓 Zamykanie ticketa za 5 sekund...", ephemeral=False)
        await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
        
        # Logika archiwizacji lub usuwania
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket zamknięty przez użytkownika/moderację.")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_tickets", description="Konfiguruje wiadomość startową ticketów")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🆘 Centrum Pomocy | 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=(
                "Potrzebujesz pomocy moderatora? Masz problem z weryfikacją?\n\n"
                "Kliknij poniższy przycisk, aby otworzyć prywatne zgłoszenie.\n\n"
                "**System Weryfikacji 𝑺𝒘𝒊𝒓𝑯𝒖𝒃** — Czekamy na Ciebie!"
            ),
            color=0x5865F2
        )
        embed.set_image(url="https://twoj-link-do-logo-swirhub.png") # Możesz tu wstawić link do grafiki
        
        await interaction.response.send_message("Wysyłanie panelu...", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketCreateView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
