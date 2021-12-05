from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.cmds import tempban
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'ban'


def description():
    return 'Ban a user from the server permanently.'


async def _action(ctx, reply, user_id, reason):
    await tempban.action(ctx, reply, user_id, '100y', reason, needs_approval=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        reason: Option(str, 'The note to add. Will be sent to the user in a DM as well.')
):
    await _action(ctx, Reply.slash, user_id, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*PrefixPerms.ALL_ADMINS)
async def action_prefix(ctx: ApplicationContext, user_id, reason):
    await _action(ctx, Reply.prefix, user_id, reason)


def setup(le_bot):
    le_bot.add_command(action_prefix)
