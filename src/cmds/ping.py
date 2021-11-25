from discord.ext import commands
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds.proxy_helpers import Reply


def name():
    return 'ping'


def description():
    return 'A simple parse-and-reply check.'


async def _ping(ctx, reply):
    await reply(ctx, 'Pong!')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def ping_slash(ctx):
    await _ping(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def ping_prefix(ctx):
    await _ping(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(ping_prefix)

