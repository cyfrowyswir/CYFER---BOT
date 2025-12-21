import discord
import os
from discord.ext import commands

# ⚠️ KLUCZOWE: Importujemy widok weryfikacji, żeby bot go widział w main.py
from cogs.werefikacja import VerificationView 

class SwirHub(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True 
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    # Ta funkcja MUSI być wcięta, żeby była wewnątrz klasy
    async def setup_hook(self):
        extensions = [
            "cogs.przywitanie",
            "cogs.werefikacja",
            "cogs.zaproszenia",
            "cogs.admin",
            "cogs.ogloszenia",  
            "cogs.konkursy"     
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Załadowano moduł: {ext}")
            except Exception as e:
                print(f"❌ Błąd ładowania {ext}: {e}")

        # Rejestracja widoku weryfikacji (działa po restarcie)
        # Teraz zadziała, bo dodaliśmy import na górze pliku
        self.add_view(VerificationView())
        
        # Synchronizacja komend
        try:
            await self.tree.sync()
            print("✅ Drzewo komend zsynchronizowane")
        except Exception as e:
            print(f"❌ Błąd synchronizacji: {e}")

    async def on_ready(self):
        print(f"✅ System SwirHub aktywny jako {self.user}")

bot = SwirHub()

# Komenda naprawcza (zostawiamy bez zmian, jest OK)
@bot.command()
@commands.has_permissions(administrator=True)
async def napraw(ctx):
    await ctx.send("⏳ Sprzątanie komend slash... proszę czekać.")
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        await ctx.send("💎 **Sukces!** Stare komendy usunięte. Zrób teraz **Ctrl+R** na Discordzie.")
    except Exception as e:
        await ctx.send(f"❌ Wystąpił błąd: {e}")
        print(f"Błąd naprawy: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
