import os
from pathlib import Path

import discord
from os import listdir
from os.path import dirname
from discord.ext import commands

from src.log4noah import STDOUT_LOG

intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(no_category='Available Commands')
bot = commands.Bot(command_prefix='++', case_insensitive=True, help_command=help_command, intents=intents)

LOADED_ONCE = False


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='++help | /verify'))

    global LOADED_ONCE
    if not LOADED_ONCE:
        STDOUT_LOG.info('NoahBot has come online and is ready.')
        bot.load_extension('automation.scheduled_tasks')
    LOADED_ONCE = True
    STDOUT_LOG.debug('NoahBot has automatically reloaded and is now ready again.')

cmds_path = Path(dirname(__file__)) / 'cmds'
ignored_files = ['_proxy_helpers.py']
extensions = [f.replace('.py', '') for f in listdir(cmds_path) if f not in ignored_files and not f.startswith('__')]

for extension in extensions:
    bot.load_extension('src.cmds.' + extension)
    STDOUT_LOG.debug(f'Module loaded: {extension}')

STDOUT_LOG.info('Starting bot...')
bot.run(os.getenv('BOT_TOKEN', None))
