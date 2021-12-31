from datetime import datetime
from typing import Optional

from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands
from mysql.connector import connect

from src.cmds._proxy_helpers import Reply, parse_duration_str, perform_unban_user
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.lib.schedule import schedule
from src.noahbot import bot


def name():
    return 'dispute'


def description():
    return 'Dispute a ban request by changing the ban duration, then approve it.'


async def perform_action(ctx: ApplicationContext, reply, ban_id, duration):
    try:
        ban_id = int(ban_id)
    except ValueError:
        await reply(ctx, 'Ban ID must be a number.')
        return

    if parse_duration_str(duration) is None:
        await reply(ctx, 'Could not parse duration. Malformed.')
        return

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            baseline_ts: Optional[datetime] = None
            query_str = """SELECT user_id, timestamp FROM ban_record WHERE id = %s"""
            cursor.execute(query_str, (ban_id, ))
            for row in cursor.fetchall():
                user_id = row[0]
                baseline_ts = row[1]

            new_unban_time = parse_duration_str(duration, int(baseline_ts.timestamp()))

            query_str = """UPDATE ban_record SET unban_time = %s, approved = 1 WHERE id = %s"""
            cursor.execute(query_str, (new_unban_time, ban_id))
            connection.commit()

            run_at = datetime.fromtimestamp(new_unban_time)
        bot.loop.create_task(schedule(perform_unban_user(bot.guilds[0], user_id), run_at=run_at))

    new_unban_at = datetime.fromtimestamp(new_unban_time).strftime('%B %d, %Y')
    await reply(ctx, f'Ban duration updated and approved. The member will be unbanned on {new_unban_at} UTC.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
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
