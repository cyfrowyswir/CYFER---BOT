import discord
import os
from discord.ext import commands

class SwirHub(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Automatyczne ładowanie plików z folderu cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ System SwirHub aktywny jako {self.user}")

bot = SwirHub()

@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    bot.tree.clear(guild=None)
    await bot.tree.sync()
    await ctx.send("🧹 Wyczyszczono duplikaty! Zrestartuj Discorda (Ctrl+R).")

bot.run(os.getenv('DISCORD_TOKEN'))
