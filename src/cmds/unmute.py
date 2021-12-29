from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext

from src.log4noah import STDOUT_LOG
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, RoleIDs
from src.cmds._proxy_helpers import Reply, get_user_id, remove_record


def name():
    return 'unmute'


def description():
    return 'Unmute the user removing the Muted role.'


async def perform_action(ctx: ApplicationContext, reply, user_id):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return
    await unmute_user(user_id)

    member = await bot.guilds[0].fetch_member(user_id)
    await reply(ctx, f'{member.mention} has been unmuted.', send_followup=False)


async def unmute_user(user_id):
    member = await bot.guilds[0].fetch_member(user_id)
    STDOUT_LOG.debug(f'Got member {member} with fetch_member')  # TODO    delete this

    role = bot.guilds[0].get_role(RoleIDs.MUTED)

    STDOUT_LOG.debug('About to unmute...', member=member, role=role)

    await member.remove_roles(role)
    remove_record('DELETE FROM mute_record where user_id = %s', (user_id,))


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.')
):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
