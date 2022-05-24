import os
import sentry_sdk
from os import listdir
from os.path import dirname
from pathlib import Path

import discord
from discord.ext import commands

from src.log4noah import STDOUT_LOG

intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(no_category='Available Commands')
bot = commands.Bot(command_prefix='++', case_insensitive=True, help_command=help_command, intents=intents)

LOADED_ONCE = False


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='++verify | ++help'))

    global LOADED_ONCE
    if not LOADED_ONCE:
        STDOUT_LOG.info('NoahBot has come online and is ready.')
        bot.load_extension('automation.scheduled_tasks')
        sentry_sdk.init("https://560d7d4a261f46daa9ae3146845a6d61@o415800.ingest.sentry.io/6410280", traces_sample_rate=1.0)

    LOADED_ONCE = True
    STDOUT_LOG.debug('NoahBot has automatically reloaded and is now ready again.')

cmds_path = Path(dirname(__file__)) / 'cmds'
ignored_files = ['_proxy_helpers.py']
extensions = [f.replace('.py', '') for f in listdir(cmds_path) if f not in ignored_files and not f.startswith('__')]

for extension in extensions:
    bot.load_extension('src.cmds.' + extension)
    STDOUT_LOG.debug(f'Module loaded: {extension}')
bot.load_extension('src.webhooks')
STDOUT_LOG.debug("Loaded webhook module")

STDOUT_LOG.debug(f'All pending application commands: {", ".join([c.name for c in bot.pending_application_commands])}')
STDOUT_LOG.info('Starting bot...')
bot.run(os.getenv('BOT_TOKEN', None))
