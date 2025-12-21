import discord
from discord import app_commands
from discord.ext import commands

class Zaproszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Pobieramy zaproszenia dla każdego serwera przy starcie bota
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                print(f"❌ Brak uprawnień do czytania zaproszeń na serwerze: {guild.name}")

    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        kanal_id = 1451263521995362565
        channel = member.guild.get_channel(kanal_id)
        if not channel: return

        try:
            new_invites = await member.guild.invites()
            old_invites = self.invites.get(member.guild.id, [])
            self.invites[member.guild.id] = new_invites

            inviter = None
            used_invite = None

            for invite in old_invites:
                new_invite = self.find_invite_by_code(new_invites, invite.code)
                if new_invite and new_invite.uses > invite.uses:
                    inviter = invite.inviter
                    used_invite = new_invite
                    break

            embed = discord.Embed(title="🎫 Nowe Zaproszenie!", color=0x2ecc71)
            if inviter:
                total_uses = sum(i.uses for i in new_invites if i.inviter and i.inviter.id == inviter.id)
                embed.description = (
                    f"Gracz **{inviter.name}** zaprosił użytkownika {member.mention}!\n\n"
                    f"👤 **Zapraszający:** {inviter.mention}\n"
                    f"📈 **Łącznie zaproszonych osób:** `{total_uses}`"
                )
            else:
                embed.description = f"Użytkownik {member.mention} dołączył bezpośrednio."
            
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Błąd przy on_member_join: {e}")

    # --- NOWA KOMENDA ADMINISTRACYJNA ---
    @app_commands.command(name="zaproszenia", description="Sprawdza liczbę zaproszeń danego gracza")
    @app_commands.describe(uzytkownik="Wybierz gracza, którego zaproszenia chcesz sprawdzić")
    @app_commands.checks.has_permissions(administrator=True)
    async def sprawdz_zaproszenia(self, interaction: discord.Interaction, uzytkownik: discord.Member = None):
        # Jeśli nie wybrano użytkownika, sprawdzamy osobę wpisującą komendę
        target = uzytkownik or interaction.user
        
        await interaction.response.defer(ephemeral=True) # Zapobiega błędom przy długim ładowaniu
        
        try:
            invites = await interaction.guild.invites()
            # Liczymy wszystkie użycia zaproszeń stworzonych przez danego użytkownika
            user_invites_count = sum(i.uses for i in invites if i.inviter and i.inviter.id == target.id)
            
            embed = discord.Embed(
                title="📊 Statystyki Zaproszeń",
                description=f"Użytkownik: {target.mention}\nIlość zaproszonych osób: **{user_invites_count}**",
                color=0x5865F2
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.set_footer(text=f"Sprawdzone przez: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ Nie mam uprawnień do przeglądania zaproszeń!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Wystąpił błąd: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Zaproszenia(bot))
