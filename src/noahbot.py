import os
import discord
from discord.ext import commands


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='++', case_insensitive=True, intents=intents)  # , help_command=PrettyHelp())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='NoahBot'))

extensions = [
    'moderation',
    'htb',
    'diagnostics'
]
for extension in extensions:
    bot.load_extension('src.cmds.' + extension)


# TODO: Absorb exceptions from, e.g. users running commands they don't have permissions to run
bot.run(os.getenv('BOT_TOKEN', None))
