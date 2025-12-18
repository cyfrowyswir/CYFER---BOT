import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

# --- USTAWIAJĄC TE ID, BOT BĘDZIE WIEDZIAŁ GDZIE DZIAŁAĆ ---
ID_KANALU_POWITAN = 1451263521995362564  # ID kanału powitalnego
ID_ROLI_WERYFIKACJA = 1451263520812568672 # ID roli nadawanej po kliknięciu
ID_KANALU_WERYFIKACJA = 1451263521995362557 # ID kanału gdzie stoi panel weryfikacji

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True 

bot = commands.Bot(command_prefix='!', intents=intents)
THEME_COLOR = 0x9b59b6 # Fioletowy kolor SwirHub

# Cache zaproszeń do śledzenia kto kogo zaprosił
invites = {}

# --- 1. WERYFIKACJA (STYL PRIME/DREAM) ---
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="v_btn")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLI_WERYFIKACJA)
        if role in interaction.user.roles:
            return await interaction.response.send_message("Jesteś już zweryfikowany!", ephemeral=True)
        
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Pomyślnie zweryfikowano w **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!", ephemeral=True)

# --- 2. POWITANIA + INVITE TRACKER ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(ID_KANALU_POWITAN)
    if not channel: return

    # Logika śledzenia zaproszeń
    inviter = "Nieznany"
    try:
        before = invites[member.guild.id]
        after = await member.guild.invites()
        for invite in before:
            for new_invite in after:
                if invite.code == new_invite.code and new_invite.uses > invite.uses:
                    inviter = invite.inviter.mention
                    break
        invites[member.guild.id] = after
    except: pass

    # Wygląd jak na screenie DreamCode
    emb = discord.Embed(
        title=f"💎 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 × WITAMY {member.name.upper()}",
        description=(
            f"Witaj na oficjalnym Discordzie serwera **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!\n"
            f"Mamy nadzieję, że z nami zostaniesz!\n\n"
            f"👤 **Użytkownik:** {member.mention}\n"
            f"🔗 **Zaproszony przez:** {inviter}"
        ),
        color=THEME_COLOR
    )
    # Jeśli masz link do grafiki (np. fioletowe logo), wstaw je tutaj:
    # emb.set_image(url="LINK_DO_TWOJEJ_GRAFIKI")
    emb.set_thumbnail(url=member.display_avatar.url)
    emb.set_footer(text=f"© 2021 - 2025 • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 • Jesteś {len(member.guild.members)} członkiem")
    
    await channel.send(embed=emb)

# --- 3. START I SYNCHRONIZACJA ---
@bot.event
async def on_ready():
    # Pobieranie zaproszeń na start
    for guild in bot.guilds:
        try: invites[guild.id] = await guild.invites()
        except: pass
    
    bot.add_view(VerifyView())
    print(f"✅ 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 Bot gotowy do akcji!")

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Slash commands zsynchronizowane!")

# --- 4. KOMENDA PANELU WERYFIKACJI ---
@bot.tree.command(name="setup_weryfikacja", description="Wysyła profesjonalny panel weryfikacji")
@app_commands.checks.has_permissions(administrator=True)
async def v_setup(interaction: discord.Interaction):
    emb = discord.Embed(
        title="𝑺𝒘𝒊𝒓𝑯𝒖𝒃 — Weryfikacja",
        description=(
            "Aby uzyskać dostęp do serwera, musisz się zweryfikować.\n\n"
            "Kliknij przycisk poniżej aby się zweryfikować."
        ),
        color=THEME_COLOR
    )
    # Możesz dodać obrazek weryfikacji jak na Twoim screenie:
    # emb.set_image(url="LINK_DO_GRAFIKI_WERYFIKACJA")
    
    await interaction.channel.send(embed=emb, view=VerifyView())
    await interaction.response.send_message("Panel wysłany!", ephemeral=True)

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
