from datetime import datetime
from typing import Optional

from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply, parse_duration_str


def name():
    return 'dispute'


def description():
    return 'Dispute a ban request by changing the ban duration, then approve it.'


async def perform_action(ctx: ApplicationContext, reply, ban_id, duration):
    # TODO: should also set "approved" to 1
    # TODO: when calculating the new "unban time", use `timestamp` from DB as baseline
    try:
        ban_id = int(ban_id)
    except ValueError:
        reply(ctx, 'Ban ID must be a number.')
        return

    if parse_duration_str(duration) is None:
        reply(ctx, 'Could not parse duration. Malformed.')
        return

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            unban_at: Optional[datetime] = None
            query_str = """SELECT timestamp FROM ban_record WHERE id = %s"""
            cursor.execute(query_str, (ban_id, ))
            for row in cursor.fetchall():
                unban_at = row[0]

            new_unban_time = parse_duration_str(duration, int(unban_at.timestamp()))

            query_str = """UPDATE ban_record SET unban_time = %s, approved = 1 WHERE id = %s"""
            cursor.execute(query_str, (new_unban_time, ban_id))
            connection.commit()

    new_unban_at = datetime.fromtimestamp(new_unban_time).strftime('%B %d, %Y')
    await reply(ctx, f'Ban duration updated and approved. The member will be unbanned on {new_unban_at} UTC.')


@bot.slash_command(permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        ban_id: Option(int, 'Ban ID from ban request.'),
        duration: Option(str, 'New duration of the temporary ban, from the point in time of the ban.')
):
    await perform_action(ctx, Reply.slash, ban_id, duration)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, ban_id, duration):
    await perform_action(ctx, Reply.prefix, ban_id, duration)


def setup(le_bot):
    le_bot.add_command(action_prefix)
