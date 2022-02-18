import time

from discord import Member
from mysql.connector import connect

from src.cmds._error_handling import interruptable
from src.conf import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.lib.verification import process_identification, get_user_details

cooldowns: dict[int, int] = {}

async def process_reverify(member: Member):
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with interruptable(connection.cursor()) as cursor:
            query_str = """SELECT account_identifier FROM htb_discord_link WHERE discord_user_id = %s"""
            cursor.execute(query_str, (member.id, ))
            details = cursor.fetchone()
            if details is None:
                return
    if on_cooldown(member):
        return
    htb_details = await get_user_details(details[0])
    await process_identification(None, None, htb_details, member.id)
    await set_cooldown(member)


async def on_cooldown(member: Member):
    return cooldowns.get(member.id) is not None && cooldowns[member.id] >= time.time()

async def set_cooldown(member: Member):
    cooldowns[member.id] = time.time() + 5 * 60
