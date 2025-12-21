import discord
from discord.ext import commands

class Przywitanie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # ID kanału powitalnego (zmień jeśli trzeba)
        kanal_id = 1451263521995362564 
        kanal = member.guild.get_channel(kanal_id)
        
        if kanal:
            embed = discord.Embed(
                title="✨ Nowy członek na pokładzie!",
                description=(
                    f"Witaj {member.mention} w społeczności **𝑺𝒘𝒊𝒓𝑯𝒖𝒃**!\n\n"
                    "**Co teraz warto zrobić?**\n"
                    "• Przeczytaj zasady na kanale regulaminu 📜\n"
                    "• Odblokuj dostęp w `/weryfikacja` ✅\n"
                    "• Rozgość się i baw się dobrze! 🎉"
                ),
                color=0x5865F2
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"Jesteś naszym {len(member.guild.members)} użytkownikiem!", 
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            await kanal.send(content=f"Siema {member.mention}! Miło Cię widzieć.", embed=embed)

async def setup(bot):
    await bot.add_cog(Przywitanie(bot))
