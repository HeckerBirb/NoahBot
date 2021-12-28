from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'flag'


def description():
    return "This is not the flag you're looking for..."


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, '`+-------------+`\n`| Not a flag. |`\n`+-------------+`', send_followup=False)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
