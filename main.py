import discord
import os
import asyncio
import random
import re
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from datetime import datetime

# --- KONFIGURACJA 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ---
ID_ROLI_WERYFIKACJA = 1451263520812568672 
ID_KANALU_POWITAN = 1451263521995362564   
ID_ROLI_ADMINISTRACJI = 1451263520795529338
THEME_COLOR = 0x9b59b6 # Królewski fiolet

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class SwirHubBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Rejestracja widoków dla trwałości interakcji
        self.add_view(VerifyView())
        self.add_view(TicketLauncher())
        self.add_view(TicketControlView())

    async def update_status(self):
        total = sum(g.member_count for g in self.guilds)
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"🛸 monitoruje {total} osób"
        ))

bot = SwirHubBot()

# --- 📜 MODAL: KRÓLEWSKI DEKRET (/tekst) ---
class TekstModal(Modal, title="🖋️ Redagowanie Pisma"):
    tytul = TextInput(label="Nagłówek Dekretu", placeholder="Wpisz tytuł...", min_length=1)
    tresc = TextInput(label="Treść Przesłania", style=discord.TextStyle.paragraph, placeholder="Twoje słowa...", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title=f"📜 {self.tytul.value}", 
            description=f"\n{self.tresc.value}\n", 
            color=THEME_COLOR, 
            timestamp=datetime.now()
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • Oficjalne Obwieszczenie")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Pismo zostało rozesłane!", ephemeral=True)

# --- 🎟️ SYSTEM AUDIENCJI (TICKETY PREMIUM) ---
class TicketControlView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Zakończ audiencję", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.response.send_message("🔒 Komnata zostanie zapieczętowana i usunięta za 5s...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Wybierz cel Twej wizyty...", custom_id="t_select", options=[
        discord.SelectOption(label="Pomoc Techniczna", emoji="🛠️", description="Gdy mechanizmy krainy zawiodą"),
        discord.SelectOption(label="Skarbiec (Sklep)", emoji="💰", description="Pytania o rangi i dary"),
        discord.SelectOption(label="Zgłoszenie/Skarga", emoji="⚖️", description="Dla poszukujących sprawiedliwości")
    ])
    async def callback(self, interaction, select):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await interaction.guild.create_text_channel(name=f"🆘-{interaction.user.name}", overwrites=overwrites)
        
        emb = discord.Embed(title="🏛️ PRYWATNA AUDIENCJA", color=THEME_COLOR)
        emb.description = (
            f"Witaj, wędrowcze {interaction.user.mention} w komnatach **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**.\n"
            "Strażnicy zostali powiadomieni o Twoim przybyciu.\n\n"
            f"**Temat:** `{select.values[0]}`\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "> Opisz swą sprawę z szacunkiem, a pomoc wkrótce nadejdzie."
        )
        emb.set_footer(text="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Support")
        
        await ch.send(content=f"{interaction.user.mention} | <@&{ID_ROLI_ADMINISTRACJI}>", embed=emb, view=TicketControlView())
        await interaction.response.send_message(f"✅ Otwarto Twój ticket: {ch.mention}", ephemeral=True)

# --- 🛸 BRAMA WERYFIKACJI ---
class VerifyView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Odbierz dostęp", style=discord.ButtonStyle.primary, emoji="🛸", custom_id="v_b")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🛸 Weryfikacja udana! Witaj na pokładzie.", ephemeral=True)

# --- ⚔️ NOWOCZESNE KOMENDY SLASH (CZYSTY KOD) ---

@bot.tree.command(name="tekst", description="Redaguje piękne, starożytne pismo")
async def tekst_cmd(interaction: discord.Interaction):
    # Naprawiono: Teraz używa Modala, co eliminuje błąd "Aplikacja nie reaguje"
    await interaction.response.send_modal(TekstModal())

@bot.tree.command(name="ticket", description="Rozstawia luksusowy panel ticketów")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_cmd(interaction: discord.Interaction):
    emb = discord.Embed(title="📩 POTRZEBUJESZ POMOCY?", color=THEME_COLOR)
    emb.description = (
        "Otwórz bilet, aby skontaktować się z Radą Administracji.\n"
        "Wybierz kategorię z menu poniżej, by rozpocząć audiencję."
    )
    # Usunięto martwy obrazek z Imgura, dodano elegancki divider
    emb.add_field(name="━━━━━━━━━━━━━━━━━━━━━", value="✨ Wybierz mądrze swą ścieżkę.", inline=False)
    await interaction.channel.send(embed=emb, view=TicketLauncher())
    await interaction.response.send_message("✅ Panel audiencji został postawiony.", ephemeral=True)

@bot.tree.command(name="clear", description="Oczyszcza czat z zbędnych pism")
@app_commands.checks.has_permissions(manage_messages=True)
async def clr_cmd(interaction: discord.Interaction, ilosc: int):
    await interaction.channel.purge(limit=ilosc)
    emb = discord.Embed(description=f"🧹 Magiczna miotła usunęła **{ilosc}** wiadomości.", color=THEME_COLOR)
    await interaction.response.send_message(embed=emb, ephemeral=True)

# --- 📜 EVENTY I KRONIKI ---
@bot.event
async def on_member_join(member):
    await bot.update_status()
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if channel:
        emb = discord.Embed(title="🪐 Nowa dusza w królestwie!", color=THEME_COLOR)
        emb.description = f"Witaj {member.mention}! Miło Cię widzieć w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**."
        emb.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=emb)

@bot.event
async def on_member_remove(member): await bot.update_status()

@bot.event
async def on_ready():
    await bot.update_status()
    print(f"✅ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 ONLINE")

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    # Kluczowy element: usuwa stare komendy i rejestruje nowe
    await bot.tree.sync()
    await ctx.send("✅ Kodeks komend Slash został pomyślnie zsynchronizowany!")

bot.run(os.getenv('DISCORD_TOKEN'))
