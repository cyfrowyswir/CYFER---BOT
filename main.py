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
        # 1. Ładowanie plików z folderu cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        # 2. BRUTALNE CZYSZCZENIE (usuwa stare duplikaty)
        self.tree.clear(guild=None) # Czyści komendy globalne
        await self.tree.sync() # Synchronizuje czystą listę
        print("🧹 Baza komend Slash została odświeżona.")

    async def on_ready(self):
        print(f"✅ System SwirHub aktywny jako {self.user}")

bot = SwirHub()

# Komenda ratunkowa na czacie (prefix !)
@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    await ctx.send("⏳ Trwa wymuszone sprzątanie menu komend...")
    bot.tree.clear(guild=None)
    await bot.tree.sync()
    await ctx.send("💎 Gotowe! Teraz **Koniecznie** zrób Ctrl+R na Discordzie.")

bot.run(os.getenv('DISCORD_TOKEN'))
