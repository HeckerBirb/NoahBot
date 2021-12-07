import calendar
import time

from discord.errors import Forbidden
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_URI, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, RoleIDs
from src.cmds._proxy_helpers import Reply, get_user_id, member_is_staff, parse_duration_str

"""
CREATE TABLE `mute_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` text NOT NULL,
  `moderator` varchar(42) NOT NULL,
  `unmute_time` int(42) NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `mute_record`
SELECT
    id, member, reason, moderator, unmuteTime
FROM MutedMember;
"""


def name():
    return 'mute'


def description():
    return 'Mute a person (adds the Muted role to person).'


# TODO: should have an auto-unmute functionality
async def perform_action(ctx: ApplicationContext, reply, user_id, duration, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return
    member = ctx.guild.get_member(user_id)

    if member_is_staff(member):
        await reply(ctx, 'You cannot mute another staff member.')
        return

    dur = parse_duration_str(duration)
    if dur is None:
        reply(ctx, 'Invalid duration: could not parse.', delete_after=15)
        return

    epoch_time = calendar.timegm(time.gmtime())

    if dur - epoch_time <= 0:
        reply(ctx, 'Invalid duration: cannot be in the past.', delete_after=15)
        return

    if len(reason) == 0:
        reason = 'Time to shush, innit?'

    with connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO mute_record (user_id, reason, moderator, unmute_time) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, ctx.author.id, dur))
            connection.commit()

    role = ctx.guild.get_role(RoleIDs.MUTED)
    await member.add_roles(role)
    await reply(ctx, f"{member.mention} has been muted for {duration}.")
    try:
        await member.send(f"You have been muted for {duration}. Reason:\n>>> {reason}")
    except Forbidden:
        await reply(ctx, f'Cannot DM {member.mention} due to their privacy settings.')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        duration: Option(str, 'Duration of the mute in human-friendly notation, e.g. 10m for ten minutes or 1d for one day.'),
        reason: Option(str, 'Mute reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, duration, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, duration: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, duration, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
