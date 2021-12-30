import asyncio
from datetime import datetime
from discord.ext import tasks
from mysql.connector import connect

from src.cmds._proxy_helpers import perform_unban_user, perform_unmute_user
from src.conf import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.lib.schedule import schedule
from src.log4noah import STDOUT_LOG
from src.noahbot import bot


@tasks.loop(count=1)
async def all_tasks():
    STDOUT_LOG.debug('Gathering scheduled tasks...')
    scheduled_tasks = []
    scheduled_tasks = scheduled_tasks + auto_unban()
    scheduled_tasks = scheduled_tasks + auto_unmute()
    STDOUT_LOG.debug('Gathering of scheduled tasks complete.')

    STDOUT_LOG.debug(f'Scheduling {len(scheduled_tasks)} tasks...')
    await asyncio.gather(*scheduled_tasks)
    STDOUT_LOG.debug('Scheduling completed.')


def auto_unban():
    unban_tasks = []
    now = datetime.now()
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT user_id, unban_time FROM ban_record WHERE unbanned = 0"""
            cursor.execute(query_str)

            for row in cursor.fetchall():
                # row = id, user_id, unban_time
                run_at = datetime.fromtimestamp(row[1])
                STDOUT_LOG.debug(f'Got user_id and unban timestamp from DB.', user_id=row[0], unban_ts=run_at)

                if (run_at - now).days > 365:
                    STDOUT_LOG.info(f'Skipping scheduled unban for user_id {row[0]}: is over one years into the future ({str(run_at)})')
                    continue

                unban_tasks.append(schedule(perform_unban_user(bot.guilds[0], row[0]), run_at=run_at))
                STDOUT_LOG.info(f'Scheduled unban task for user_id {row[0]} at {str(run_at)}.')

    return unban_tasks


def auto_unmute():
    unmute_tasks = []
    now = datetime.now()
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT user_id, unmute_time FROM mute_record"""
            cursor.execute(query_str)

            for row in cursor.fetchall():
                # row = id, user_id, unban_time
                run_at = datetime.fromtimestamp(row[1])
                STDOUT_LOG.debug(f'Got user_id and unmute timestamp from DB.', user_id=row[0], unmute_ts=run_at)

                if (run_at - now).days > 365:
                    STDOUT_LOG.info(f'Skipping scheduled unmute for user_id {row[0]}: is over one years into the future ({str(run_at)})')
                    continue

                unmute_tasks.append(schedule(perform_unmute_user(bot.guilds[0], row[0]), run_at=run_at))
                STDOUT_LOG.info(f'Scheduled unmute task for user_id {row[0]} at {str(run_at)}.')

    return unmute_tasks


def setup(_):
    all_tasks.start()
