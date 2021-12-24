import calendar
import re
import time

import discord
from discord.commands.context import ApplicationContext
from typing import Union, Optional, Tuple, Any

from mysql.connector import connect

from src.conf import RoleIDs, MYSQL_URI, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.log4noah import STDOUT_LOG


class Reply:
    @staticmethod
    def _log_call_and_msg(ctx, msg, **kwargs):
        STDOUT_LOG.debug(f'<Reply> cmd: "{ctx.command.name}", user: "{ctx.author.name}" ({ctx.author.id}), msg: "{msg}", kwargs: {kwargs}')

    """ Proxy for ctx.send and ctx.respond. Accepts same kwargs as the discord.InteractionResponse.send_message() does. """
    @staticmethod
    async def slash(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.respond(content=msg, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.send(content=msg, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)


def get_user_id(user_id: Union[str, discord.Member]) -> Optional[int]:
    """ Get the user ID given a string of the ID, a string of the representation of the user mention, or a Discord Member object. """
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return None

    return user_id


def parse_duration_str(duration: str, baseline_ts: int = None) -> Optional[int]:
    """
    Converts an arbitrary measure of time, e.g. "3w" to a timestamp in seconds since 1970/01/01.
    Uses baseline_ts instead of the current time, if provided.
    """
    dur = re.compile(r'(-?(?:\d+\.?\d*|\d*\.?\d+)(?:e[-+]?\d+)?)\s*([a-z]*)', re.IGNORECASE)
    units = {'s': 1}
    units['m'] = units['s'] * 60
    units['h'] = units['hr'] = units['m'] * 60
    units['d'] = units['day'] = units['h'] * 24
    units['wk'] = units['w'] = units['d'] * 7
    units['month'] = units['months'] = units['mo'] = units['d'] * 30
    units['y'] = units['yr'] = units['d'] * 365
    sum_seconds = 0

    while duration:
        m = dur.match(duration)
        if not m:
            return None
        duration = duration[m.end():]
        sum_seconds += int(m.groups()[0]) * units.get(m.groups()[1], 1)

    if baseline_ts is None:
        epoch_time = calendar.timegm(time.gmtime())
    else:
        epoch_time = baseline_ts
    return epoch_time + sum_seconds


def member_is_staff(member: discord.Member) -> bool:
    """ Checks if a member has any of the Administrator or Moderator roles defined in the RoleIDs class. """
    for role in member.roles:
        if role.id in RoleIDs.ALL_ADMINS + RoleIDs.ALL_MODS:
            return True

    return False


def remove_record(delete_query: str, id_to_remove: Tuple[Any, ...]) -> None:
    """ Delete a record from the database, given a one tuple of values for the delete query to use. """
    with connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            cursor.execute(delete_query, id_to_remove)
            connection.commit()
