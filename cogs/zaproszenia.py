import discord
from discord.ext import commands
from discord import app_commands

class Zaproszenia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cache zaproszeń: {guild_id: {invite_code: uses}}
        self.invites_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Budowanie wstępnego cache zaproszeń dla wszystkich serwerów
        for guild in self.bot.guilds:
            try:
                self.invites_cache[guild.id] = {invite.code: invite.uses for invite in await guild.invites()}
            except discord.Forbidden:
                print(f"Brak uprawnień do czytania zaproszeń na serwerze: {guild.name}")
        print("System Zaproszeń: Cache został załadowany.")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild.id not in self.invites_cache:
            self.invites_cache[invite.guild.id] = {}
        self.invites_cache[invite.guild.id][invite.code] = invite.uses

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.id in self.invites_cache:
            self.invites_cache[invite.guild.id].pop(invite.code, None)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invites_before = self.invites_cache.get(member.guild.id, {})
        invites_after = await member.guild.invites()
        
        inviter = None
        for invite in invites_after:
            if invite.code in invites_before and invite.uses > invites_before[invite.code]:
                inviter = invite.inviter
                # Aktualizacja cache
                self.invites_cache[member.guild.id][invite.code] = invite.uses
                break
        
        # Opcjonalne: Logowanie do kanału (możesz ustawić ID kanału)
        # channel = member.guild.get_channel(ID_KANALU)
        # if inviter and channel:
        #    await channel.send(f"📥 **{member}** dołączył dzięki zaproszeniu od **{inviter}**!")

    @app_commands.command(name="zaproszenia", description="Sprawdza liczbę Twoich zaproszeń lub wybranego użytkownika")
    @app_commands.describe(uzytkownik="Użytkownik, którego statystyki chcesz sprawdzić")
    async def zaproszenia(self, interaction: discord.Interaction, uzytkownik: discord.Member = None):
        target = uzytkownik or interaction.user
        
        total_invites = 0
        guild_invites = await interaction.guild.invites()
        
        for invite in guild_invites:
            if invite.inviter == target:
                total_invites += invite.uses

        embed = discord.Embed(
            title="Statystyki Zaproszeń 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=f"Statystyki dla użytkownika: {target.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Liczba zaproszonych osób", 
            value=f"**{total_invites}** użytkowników", 
            inline=False
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(
            text="System Zaproszeń • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", 
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="top-zaproszenia", description="Pokazuje listę osób z największą liczbą zaproszeń")
    async def top_zaproszenia(self, interaction: discord.Interaction):
        guild_invites = await interaction.guild.invites()
        invite_counts = {}

        for invite in guild_invites:
            if invite.inviter:
                inviter_name = f"{invite.inviter.name}#{invite.inviter.discriminator}" if invite.inviter.discriminator != "0" else invite.inviter.name
                invite_counts[inviter_name] = invite_counts.get(inviter_name, 0) + invite.uses

        # Sortowanie od największej liczby
        sorted_invites = sorted(invite_counts.items(), key=lambda item: item[1], reverse=True)[:10]

        description = ""
        for i, (name, count) in enumerate(sorted_invites, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
            description += f"{emoji} **{i}. {name}** — `{count}` zaproszeń\n"

        if not description:
            description = "Brak danych o zaproszeniach."

        embed = discord.Embed(
            title="Ranking Zaproszeń 𝑺𝒘𝒊𝒓𝑯𝒖𝒃",
            description=description,
            color=discord.Color.gold()
        )
        
        embed.set_footer(
            text="Top Zaproszenia • 𝑺𝒘𝒊𝒓𝑯𝒖𝒃", 
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Zaproszenia(bot))
