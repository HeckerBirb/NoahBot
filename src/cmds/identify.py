from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply


# TODO: This should maybe be a PR to "Hack The Box" bot instead of exist in here.
def name():
    return 'identify'


def description():
    return 'Identify yourself on the HTB Discord server by linking your HTB account ID to your Discord user ID.'


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
