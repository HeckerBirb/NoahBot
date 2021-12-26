import datetime
import time

from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms
from src.cmds._proxy_helpers import Reply

START_TIME: float


def name():
    return 'uptime'


def description():
    return 'Prints the uptime of the bot.'


async def perform_action(ctx: ApplicationContext, reply):
    global START_TIME

    now = time.time()
    difference = int(now - START_TIME)
    uptime = str(datetime.timedelta(seconds=difference))
    await reply(ctx, f'Uptime: {uptime}')


@bot.slash_command(permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    global START_TIME
    START_TIME = time.time()
    le_bot.add_command(action_prefix)
