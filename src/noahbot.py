import os
from pathlib import Path

import discord
from os import listdir
from os.path import isfile, join, dirname
from discord.ext import commands

intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(no_category='Available Commands')
bot = commands.Bot(command_prefix='++', case_insensitive=True, help_command=help_command, intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='NoahBot'))

cmds_path = Path(dirname(__file__)) / 'cmds'
ignored_files = ['proxy_helpers.py']
extensions = [f.replace('.py', '') for f in listdir(cmds_path) if f not in ignored_files and not f.startswith('__')]

for extension in extensions:
    bot.load_extension('src.cmds.' + extension)


# TODO: Absorb exceptions from, e.g. users running commands they don't have permissions to run
bot.run(os.getenv('BOT_TOKEN', None))
