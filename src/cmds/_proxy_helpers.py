import calendar
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Union, Optional, Tuple, Any

import discord
from discord import Forbidden, HTTPException, NotFound
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.conf import RoleIDs, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, HTB_URL, ChannelIDs
from src.lib.schedule import schedule
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
    async def slash(ctx: ApplicationContext, msg=None, ephemeral=False, send_followup=False, **kwargs):
        if send_followup:
            await ctx.send_followup(content=msg, ephemeral=ephemeral, **kwargs)
        else:
            await ctx.respond(content=msg, ephemeral=ephemeral, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, ephemeral=False, send_followup=False, **kwargs):
        # DO NOT remove named params ephemeral or send_followup. ApplicationContext.send(...) does not like these, so they must be "filtered away".
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


async def force_get_member(guild: discord.Guild, user_id: int) -> Optional[discord.Member]:
    """ Query Discord forcefully (no cache) for the user and return, if found. Otherwise return None. """
    try:
        STDOUT_LOG.debug(f'Forcefully obtaining member with ID {user_id} (no cache).')
        member = await guild.fetch_member(user_id)
        STDOUT_LOG.debug(f'Got member "{member.mention}"')
        return member
    except NotFound as ex:
        STDOUT_LOG.info(f'Could not find member with id {user_id} on the server. Exception: {ex}')
        return None


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


async def perform_temp_ban(bot, ctx, reply, user_id, duration, reason, needs_approval=True, banned_by_bot=False, send_followup=False):
    guild = bot.guilds[0]
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=send_followup)
        return

    if len(reason) == 0:
        reason = 'No reason given...'

    member = guild.get_member(user_id)
    if member is not None and member_is_staff(member):
        await reply(ctx, 'You cannot ban another staff member.', send_followup=send_followup)
        return

    dur = parse_duration_str(duration)
    if dur is None:
        await reply(ctx, 'Invalid duration: could not parse.', delete_after=15)
        return

    epoch_time = calendar.timegm(time.gmtime())

    if dur - epoch_time <= 0:
        await reply(ctx, 'Invalid duration: cannot be in the past.', delete_after=15)
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
                f'You have been banned from {guild.name} for a duration of {duration}. To appeal the ban, please reach out to an Administrator.\n'
                f'Following is the reason given:\n>>> {reason}\n')
    except Forbidden as ex:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...', send_followup=send_followup)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
    except HTTPException as ex:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.", send_followup=send_followup)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
        return

    await guild.ban(PretendSnowflake(user_id), reason=reason)

    if not needs_approval:
        if member is not None:
            await reply(ctx, f'{member.display_name} has been banned permanently.', send_followup=send_followup)
        else:
            await reply(ctx, f'User {user_id} has been banned permanently.', send_followup=send_followup)
        STDOUT_LOG.info(f'User {user_id} has been banned permanently.')
        run_at = datetime.fromtimestamp(dur)
        bot.loop.create_task(schedule(perform_unban_user(bot.guilds[0], user_id), run_at=run_at))
        return

    else:
        if member is not None:
            await reply(ctx, f'{member.display_name} has been banned for a duration of {duration}.', send_followup=send_followup)
        else:
            await reply(ctx, f'{user_id} has been banned for a duration of {duration}.', send_followup=send_followup)
        member_name = member.name if member is not None else user_id
        embed = discord.Embed(
            title=f"Ban request #{ban_id}",
            description=f'{ctx.author.name} would like to ban {member_name} for {duration}. Reason: {reason}'
        )
        embed.set_thumbnail(url=f'{HTB_URL}/images/logo600.png')
        embed.add_field(name='Approve duration:', value=f'++approve {ban_id}', inline=True)
        embed.add_field(name='Change duration:', value=f'++dispute {ban_id} <duration>', inline=True)
        embed.add_field(name='Deny and unban:', value=f'++deny {ban_id}', inline=True)
        await guild.get_channel(ChannelIDs.SR_MODERATOR).send(embed=embed)


async def perform_unban_user(guild, user_id):
    user = await force_get_member(guild, user_id)

    if user is None:
        STDOUT_LOG.info(f'User ID {user_id} not found on Discord. Consider removing entry from DB...')
        return

    try:
        await guild.unban(user)
        STDOUT_LOG.info(f'Unbanned user {user.mention} ({user_id}).')
    except Forbidden as ex:
        STDOUT_LOG.error(f'Permission denied when trying to unban user with ID {user_id}: {ex}')
        return None
    except HTTPException as ex:
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
        return None
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as co:
        with co.cursor() as cu:
            cu.execute("""UPDATE ban_record SET unbanned = 1 WHERE user_id = %s""", (user_id,))
            co.commit()
            STDOUT_LOG.debug(f'Set unbanned=1 for user_id={user_id}')
    return user


async def perform_unmute_user(guild, user_id):
    member = await force_get_member(guild, user_id)
    role = guild.get_role(RoleIDs.MUTED)

    if member is not None:
        # No longer on the server - cleanup, but don't attempt to remove a role
        STDOUT_LOG.info(f'Unmuting {member}.')
        await member.remove_roles(role)
    remove_record('DELETE FROM mute_record where user_id = %s', (user_id,))


async def perform_infraction_record(ctx, reply, guild, user_id, weight, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return
    member = guild.get_member(user_id)

    if len(reason) == 0:
        await reply(ctx, 'The reason is empty. Try again...', send_followup=False)
        return

    moderator = ctx.author.id
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER,
                 password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO infraction_record (user_id, reason, weight, moderator) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, weight, moderator))
            connection.commit()

    await reply(ctx, f'{member.mention} has been warned with a strike weight of {weight}.', send_followup=False)

    try:
        await member.send(
            f'You have been warned on {guild.name} with a strike value of {weight}. After a total value of 3, permanent exclusion from the server may be enforced.\n'
            f'Following is the reason given:\n>>> {reason}\n')
    except Forbidden as ex:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...',
                    send_followup=True)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
    except HTTPException as ex:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.",
                    send_followup=True)
        STDOUT_LOG.warn(f'HTTPException when trying to unban user with ID {user_id}: {ex}')
