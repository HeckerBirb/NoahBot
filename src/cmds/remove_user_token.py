from discord.ext import commands
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds.proxy_helpers import Reply


def name():
    return 'remove_user_token'


def description():
    return 'Remove all records of identification the user has made, allowing them to link a new Discord or HTB account together.'


async def perform_action(ctx, reply):
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
