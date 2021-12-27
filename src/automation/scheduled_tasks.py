import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
from mysql.connector import connect
from src.cmds.unban import unban_user
from src.cmds.unmute import unmute_user
from src.conf import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.lib.schedule import schedule
from src.log4noah import STDOUT_LOG


@tasks.loop(count=1)
async def all_tasks():
    STDOUT_LOG.debug('Scheduling all automated tasks...')
    await auto_unban()
    STDOUT_LOG.debug('Scheduling completed.')


async def auto_unban():
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

                unban_tasks.append(schedule(unban_user(row[0]), run_at=run_at))
                STDOUT_LOG.info(f'Scheduled unban task for user_id {row[0]} at {str(run_at)}.')

    await asyncio.gather(*unban_tasks)


async def auto_unmute():
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

                unmute_tasks.append(schedule(unmute_user(row[0]), run_at=run_at))
                STDOUT_LOG.info(f'Scheduled unmute task for user_id {row[0]} at {str(run_at)}.')

    await asyncio.gather(*unmute_tasks)


def setup(_):
    all_tasks.start()
