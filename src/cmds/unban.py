from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply, get_user_id, perform_unban_user
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.noahbot import bot


def name():
    return 'unban'


def description():
    return 'Unbans a user from the server.'


async def perform_action(ctx: ApplicationContext, reply, user_id):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return

    user = await perform_unban_user(bot.guilds[0], user_id)
    if user is None:
        await reply(ctx, f'Failed to unban user {user_id}. See server logs for more info.', send_followup=False)
        return

    await reply(ctx, f'Member {user.name} ({user.id}) has been unbanned.', send_followup=False)


@bot.slash_command(
    guild_ids=[GUILD_ID],
    permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR, SlashPerms.HTB_SUPPORT],
    name=name(),
    description=description()
)
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS + PrefixPerms.ALL_HTB_SUPPORT))
async def action_prefix(ctx: ApplicationContext, user_id):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
