from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.errors import Forbidden, HTTPException
from discord.ext import commands

from src.cmds._proxy_helpers import Reply, get_user_id
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.log4noah import STDOUT_LOG
from src.noahbot import bot


def name():
    return 'kick'


def description():
    return 'Kick a user from the server.'


async def perform_action(ctx: ApplicationContext, reply, user_id, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return
    member = bot.guilds[0].get_member(user_id)

    if len(reason) == 0:
        reason = 'No reason given...'

    try:
        await member.send(
            f'You have been kicked from {bot.guilds[0].name} for the following reason:\n>>> {reason}\n')
    except Forbidden as ex:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to kick them...', send_followup=False)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
    except HTTPException as ex:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.", send_followup=False)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
        return

    await bot.guilds[0].kick(user=member, reason=reason)
    await reply(ctx, f'{member.name} got the boot!', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),  # type: ignore
        reason: Option(str, 'Kick reason. Will be sent to the user in a DM as well.')  # type: ignore
):
    await perform_action(ctx, Reply.slash, user_id, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id, *reason):
    await perform_action(ctx, Reply.prefix, user_id, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
