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
        # Ładowanie modułów z folderu cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Załadowano moduł: {filename}")
                except Exception as e:
                    print(f"❌ Błąd modułu {filename}: {e}")
        
        # Automatyczna synchronizacja przy starcie
        await self.tree.sync()

    async def on_ready(self):
        print(f"✅ System SwirHub aktywny jako {self.user}")

bot = SwirHub()

# POPRAWIONA KOMENDA NAPRAWCZA
@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    await ctx.send("⏳ Sprzątanie komend slash... proszę czekać.")
    try:
        # Usuwamy komendy przez przypisanie pustej listy i synchronizację
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        await ctx.send("💎 **Sukces!** Stare komendy usunięte. Zrób teraz **Ctrl+R** na Discordzie.")
    except Exception as e:
        await ctx.send(f"❌ Wystąpił błąd: {e}")
        print(f"Błąd naprawy: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
