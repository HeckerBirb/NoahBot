import os
import discord
from discord.ext import commands


intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(no_category='Available Commands')
bot = commands.Bot(command_prefix='++', case_insensitive=True, help_command=help_command, intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='NoahBot'))

extensions = [
    'mute',
    'htb',
    'ping'
]
for extension in extensions:
    bot.load_extension('src.cmds.' + extension)


# TODO: Absorb exceptions from, e.g. users running commands they don't have permissions to run
bot.run(os.getenv('BOT_TOKEN', None))
