import discord
from discord.ext import commands

class Przywitanie(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        WELCOME_CHANNEL_ID = 123456789012345678 # ZMIEŃ NA SWOJE ID
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel: return

        embed = discord.Embed(
            title="Witamy na naszym discordzie!",
            description=(
                f"**𝑺 𝑾 𝑰 𝑹 𝑯 𝑼 Ｂ**\n\n"
                f"👋 Witamy Cię **{member.name}** na discordzie serwera **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**\n\n"
                f"🌟 Jest on/a: **{member.guild.member_count}** osobą na discordzie!"
            ),
            color=discord.Color.from_rgb(255, 0, 255)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="© Copyright by 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 2022-2025")
        await channel.send(content=f"Witaj {member.mention}!", embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Przywitanie(bot))
