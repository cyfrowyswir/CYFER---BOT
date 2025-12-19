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
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        # Próbujemy synchronizować, ale nie pozwalamy, by błąd zawiesił bota
        try:
            await self.tree.sync()
            print("✅ Synchronizacja przy starcie zakończona.")
        except Exception as e:
            print(f"⚠️ Nie udało się zsynchronizować przy starcie: {e}")

    async def on_ready(self):
        print(f"✅ SwirHub aktywny jako {self.user}")

bot = SwirHub()

@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    await ctx.send("🧹 Rozpoczynam czyszczenie... Sprawdź logi na Koyeb, jeśli to potrwa zbyt długo.")
    try:
        bot.tree.clear(guild=None)
        await bot.tree.sync()
        await ctx.send("💎 Gotowe! Zrestartuj teraz Discorda (Ctrl+R).")
    except Exception as e:
        await ctx.send(f"❌ Błąd krytyczny: {e}")
        print(f"Błąd synchronizacji: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
