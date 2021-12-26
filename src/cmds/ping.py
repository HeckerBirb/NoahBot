from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'ping'


def description():
    return 'A simple parse-and-reply check.'


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, 'Pong!')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR, SlashPerms.HTB_STAFF], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS + PrefixPerms.HTB_STAFF))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)

