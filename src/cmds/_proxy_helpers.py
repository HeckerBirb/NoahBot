import calendar
import re
import time
from dataclasses import dataclass
from datetime import datetime

import discord
from discord import Forbidden, HTTPException
from discord.commands.context import ApplicationContext
from typing import Union, Optional, Tuple, Any

from mysql.connector import connect

from src.conf import RoleIDs, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, HTB_URL, ChannelIDs
from src.log4noah import STDOUT_LOG


@dataclass
class PretendSnowflake:
    id: int


class Reply:
    @staticmethod
    def _log_call_and_msg(ctx, msg, **kwargs):
        STDOUT_LOG.debug(f'<Reply> cmd: "{ctx.command.name}", user: "{ctx.author.name}" ({ctx.author.id}), msg: "{msg}", kwargs: {kwargs}')

    """ Proxy for ctx.send and ctx.respond. Accepts same kwargs as the discord.InteractionResponse.send_message() does. """
    @staticmethod
    async def slash(ctx: ApplicationContext, msg=None, ephemeral=False, **kwargs):
        await ctx.respond(content=msg, ephemeral=ephemeral, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, ephemeral=None, **kwargs):
        # Note: ephemeral is unused purposefully (ctx.send doesn't support it, but I wanna stay DRY).
        await ctx.send(content=msg, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)


def get_user_id(user_id: Union[str, discord.Member]) -> Optional[int]:
    """ Get the user ID given a string of the ID, a string of the representation of the user mention, or a Discord Member object. """
    if user_id is None:
        return None
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
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            cursor.execute(delete_query, id_to_remove)
            connection.commit()


async def perform_temp_ban(bot, ctx, reply, user_id, duration, reason, needs_approval=True, banned_by_bot=False):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return

    if len(reason) == 0:
        reason = 'No reason given...'

    member = bot.guilds[0].get_member(user_id)
    if member is not None and member_is_staff(member):
        await reply(ctx, 'You cannot ban another staff member.')
        return

    dur = parse_duration_str(duration)
    if dur is None:
        reply(ctx, 'Invalid duration: could not parse.', delete_after=15)
        return

    epoch_time = calendar.timegm(time.gmtime())

    if dur - epoch_time <= 0:
        reply(ctx, 'Invalid duration: cannot be in the past.', delete_after=15)
        return

    ban_id = -1
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO ban_record (user_id, reason, moderator, unban_time, approved) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, ctx.author.id, dur, 0 if needs_approval else 1))
            connection.commit()
            cursor.execute('SELECT id FROM ban_record WHERE user_id = %s AND unban_time = %s', (user_id, dur))
            for row in cursor.fetchall():
                ban_id = row[0]

            query_str = """INSERT INTO infraction_record (user_id, reason, weight, moderator, date) VALUES (%s, %s, %s, %s, %s)"""
            banned_by = bot.user.id if banned_by_bot else ctx.author.id
            cursor.execute(query_str, (user_id, f'Previously banned for: {reason}', 0, banned_by, datetime.date(datetime.now())))
            connection.commit()

    try:
        if member is not None:
            await member.send(
                f'You have been banned from {bot.guilds[0].name} for a duration of {duration}. To appeal the ban, please reach out to an Administrator.\n'
                f'Following is the reason given:\n>>> {reason}\n')
    except Forbidden:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...')
    except HTTPException:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.")
        return

    await bot.guilds[0].ban(PretendSnowflake(user_id), reason=reason)

    if not needs_approval:
        if member is not None:
            await reply(ctx, f'{member.display_name} has been banned permanently.')
        else:
            await reply(ctx, f'{user_id} has been banned permanently.')
        return

    else:
        if member is not None:
            await reply(ctx, f'{member.display_name} has been banned for a duration of {duration}.')
        else:
            await reply(ctx, f'{user_id} has been banned for a duration of {duration}.')
        member_name = member.name if member is not None else user_id
        embed = discord.Embed(
            title=f"Ban request #{ban_id}",
            description=f'{ctx.author.name} would like to ban {member_name} for {duration}. Reason: {reason}'
        )
        embed.set_thumbnail(url=f'{HTB_URL}/images/logo600.png')
        embed.add_field(name='Approve duration:', value=f'++approve {ban_id}', inline=True)
        embed.add_field(name='Change duration:', value=f'++dispute {ban_id} <duration>', inline=True)
        embed.add_field(name='Deny and unban:', value=f'++deny {ban_id}', inline=True)
        await bot.guilds[0].get_channel(ChannelIDs.SR_MODERATOR).send(embed=embed)
