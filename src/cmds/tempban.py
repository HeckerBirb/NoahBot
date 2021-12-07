import calendar
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.errors import Forbidden, HTTPException
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_URI, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, HTB_URL, \
    ChannelIDs
from src.cmds._proxy_helpers import Reply, get_user_id, parse_duration_str, member_is_staff

"""
CREATE TABLE `ban_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` text NOT NULL,
  `moderator` varchar(42) NOT NULL,
  `unban_time` int(42) NOT NULL,
  `approved` boolean NOT NULL,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

INSERT INTO `ban_record`
SELECT
    id, member, reason, moderator, unbanTime, CASE WHEN approved = 1 THEN 1 ELSE 0 END as approved, CURRENT_TIMESTAMP
FROM BanRecords;
"""


def name():
    return 'tempban'


def description():
    return 'Ban a user from the server temporarily.'


# TODO: should have an auto-unban functionality
async def perform_action(ctx, reply, user_id, duration, reason, needs_approval=True):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return
    member = ctx.guild.get_member(user_id)

    if len(reason) == 0:
        reason = 'No reason given...'

    if member_is_staff(member):
        await reply(ctx, 'You cannot ban another staff member...')
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
    with connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO ban_record (user_id, reason, moderator, unban_time, approved) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, ctx.author.id, dur, 0 if needs_approval else 1))
            connection.commit()
            cursor.execute('SELECT id FROM ban_record WHERE user_id = %s AND unban_time = %s', (user_id, dur))
            for row in cursor.fetchall():
                ban_id = row[0]

            query_str = """INSERT INTO infraction_record (user_id, reason, weight, moderator, date) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, f'Previously banned for: {reason}', 0, ctx.author.id, datetime.date(datetime.now())))
            connection.commit()

    try:
        await member.send(
            f'You have been banned from {ctx.guild.name} for a duration of {duration}. To appeal the ban, please reach out to an Administrator.\n'
            f'Following is the reason given:\n>>> {reason}\n')
    except Forbidden:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...')
    except HTTPException:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.")
        return

    await ctx.guild.ban(member, reason=reason)

    if not needs_approval:
        await reply(ctx, f'{member.display_name} has been banned permanently.')
        return

    else:
        await reply(ctx, f'{member.display_name} has been banned for a duration of {duration}.')
        embed = discord.Embed(
            title=f"Ban request #{ban_id}",
            description=f'{ctx.author.name} would like to ban {member.name} for {duration}. Reason: {reason}'
        )
        embed.set_thumbnail(url=f'{HTB_URL}/images/logo600.png')
        embed.add_field(name='Approve duration:', value=f'/approve {ban_id}', inline=True)
        embed.add_field(name='Change duration:', value=f'/dispute {ban_id} <duration>', inline=True)
        embed.add_field(name='Deny and unban:', value=f'/deny {ban_id}', inline=True)
        await ctx.guild.get_channel(ChannelIDs.SR_MODERATOR).send(embed=embed)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        duration: Option(str, 'Duration of the ban in human-friendly notation, e.g. 2mo for two months or 3w for three weeks.'),
        reason: Option(str, 'Ban reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, duration, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, duration: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, duration, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
