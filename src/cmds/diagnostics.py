from discord.ext import commands
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds.slash_prefix_factory import Reply


def get_description():
    return 'A simple parse-and-respond check'


def get_name():
    return 'ping'


async def _ping(ctx, reply):
    await reply(ctx, 'pong')


@bot.slash_command(
    guild_ids=[GUILD_ID],
    permissions=[SlashPerms.ADMINISTRATORS, SlashPerms.MODERATORS],
    name=get_name(),
    description=get_description()
)
async def ping_slash(ctx):
    await _ping(ctx, Reply.SLASH)


@commands.command(name=get_name(), category='Diagnostics', help='A simple parse-and-reply check.')
@commands.has_any_role(*(PrefixPerms.ADMINISTRATORS + PrefixPerms.MODERATORS))
async def ping_prefix(ctx):
    await _ping(ctx, Reply.PREFIX)


def setup(le_bot):
    le_bot.add_command(ping_prefix)

