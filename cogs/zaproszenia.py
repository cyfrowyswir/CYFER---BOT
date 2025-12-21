import discord
from discord import app_commands
from discord.ext import commands

class Zaproszenia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except discord.Forbidden:
                print(f"❌ Brak uprawnień do zaproszeń na: {guild.name}")

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

            embed = discord.Embed(
                title="✨ Nowe dołączenie przez zaproszenie!",
                color=0x2ecc71
            )

            if inviter:
                # Liczymy wszystkie zaproszenia danej osoby
                total_uses = sum(i.uses for i in new_invites if i.inviter and i.inviter.id == inviter.id)
                
                # Dokładna treść, o którą prosiłeś:
                embed.description = (
                    f"👤 Użytkownik {member.mention} dołączył!\n"
                    f"📩 Zaproszenie od: {inviter.mention}\n\n"
                    f"📈 Osoba, która wysłała mu zaproszenie, ma już zaproszone: **{total_uses}** osób."
                )
            else:
                embed.description = f"👤 Użytkownik {member.mention} dołączył bez użycia kodu (lub przez Vanity URL)."
                embed.color = 0x95a5a6

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID Użytkownika: {member.id}", icon_url=member.guild.icon.url if member.guild.icon else None)
            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Błąd zaproszeń: {e}")

    @app_commands.command(name="zaproszenia", description="Sprawdza statystyki zaproszeń")
    @app_commands.checks.has_permissions(administrator=True)
    async def sprawdz_zaproszenia(self, interaction: discord.Interaction, uzytkownik: discord.Member = None):
        target = uzytkownik or interaction.user
        await interaction.response.defer(ephemeral=True)
        
        try:
            invites = await interaction.guild.invites()
            user_invites_count = sum(i.uses for i in invites if i.inviter and i.inviter.id == target.id)
            
            embed = discord.Embed(
                title="📊 Statystyki Zaproszeń",
                description=f"Użytkownik: {target.mention}\nIlość zaproszonych osób: **{user_invites_count}**",
                color=0x5865F2
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send("❌ Błąd uprawnień.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Zaproszenia(bot))
