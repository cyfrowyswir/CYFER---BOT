import discord
import os
from discord.ext import commands

class SwirHub(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True # KLUCZOWE dla komend z "!"
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        # Automatyczne ładowanie cogsów z folderu
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Załadowano moduł: {filename}")
                except Exception as e:
                    print(f"❌ Błąd modułu {filename}: {e}")
        
        # Wymuszona synchronizacja przy starcie, aby naprawić menu slash
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ SwirHub gotowy: {self.user}")

bot = SwirHub()

# Komenda ratunkowa, jeśli automatyczna synchronizacja zawiedzie
@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    await ctx.send("⏳ Sprzątanie komend...")
    bot.tree.clear(guild=None)
    await bot.tree.sync()
    await ctx.send("💎 Gotowe! Zrestartuj Discorda (Ctrl+R).")

bot.run(os.getenv('DISCORD_TOKEN'))
