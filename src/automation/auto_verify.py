import time

from discord import Member
from mysql.connector import connect

from src.conf import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.lib.verification import process_identification, get_user_details
from src.log4noah import STDOUT_LOG

cooldowns: dict[int, float] = {}


async def process_reverify(member: Member):
    member_token = None
    if await on_cooldown(member):
        return

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT account_identifier FROM htb_discord_link WHERE discord_user_id = %s ORDER BY id DESC LIMIT 1"""
            cursor.execute(query_str, (member.id, ))
            for row in cursor.fetchall():
                member_token = row[0]

    if member_token is None:
        return

    STDOUT_LOG.debug(f'Processing reverify of member {member.name}.')
    htb_details = await get_user_details(member_token)
    if htb_details is None:
        return

    await process_identification(None, None, htb_details, member.id)
    await set_cooldown(member)
    await clear_cooldowns()


async def on_cooldown(member: Member):
    return cooldowns.get(member.id) is not None and cooldowns[member.id] >= time.time()


async def set_cooldown(member: Member):
    global cooldowns
    duration = 30 * 60
    STDOUT_LOG.debug(f'Putting member {member.name} ({member.id}) on {int(duration / 60)} min cooldown.')
    cooldowns[member.id] = time.time() + duration


async def clear_cooldowns():
    global cooldowns
    expired_cooldowns = list(filter(lambda val: val[1] <= time.time(), cooldowns.items()))
    for i, _ in expired_cooldowns:
        del cooldowns[i]

