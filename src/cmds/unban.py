from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.log4noah import STDOUT_LOG
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply, get_user_id
from discord.errors import NotFound, Forbidden, HTTPException


def name():
    return 'unban'


def description():
    return 'Unbans a user from the server.'


async def perform_action(ctx: ApplicationContext, reply, user_id):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return

    user = await unban_user(user_id)
    if user is None:
        await reply(ctx, f'Failed to unban user {user_id}. See server logs for more info.', send_followup=False)
        return

    await reply(ctx, f'Member {user.name} ({user.id}) has been unbanned.', send_followup=False)


async def unban_user(user_id):
    guild = bot.guilds[0]
    user = bot.get_user(user_id)

    if user is None:
        STDOUT_LOG.info(f'User ID {user_id} not found on Discord. Consider removing entry from DB...')
        return

    try:
        await guild.unban(user)
        STDOUT_LOG.info(f'Unbanned user {user.mention} ({user_id}).')
    except Forbidden:
        STDOUT_LOG.error(f'Permission denied when trying to unban user with ID {user_id}.')
        return None
    except HTTPException:
        STDOUT_LOG.error(f'HTTPException when trying to unban user with ID {user_id}.')
        return None
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as co:
        with co.cursor() as cu:
            cu.execute("""UPDATE ban_record SET unbanned = 1 WHERE user_id = %s""", (user_id,))
            co.commit()
            STDOUT_LOG.debug(f'Set unbanned=1 for user_id={user_id}')
    return user


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, user_id):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
