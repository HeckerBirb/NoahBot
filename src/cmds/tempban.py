import calendar
import time

from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.errors import Forbidden
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_URI, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply, get_user_id, parse_duration_str

"""
CREATE TABLE `ban_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` text NOT NULL,
  `moderator` varchar(42) NOT NULL,
  `unban_time` int(42) NOT NULL,
  `approved` boolean NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `ban_record`
SELECT
    id, member, reason, moderator, unbanTime, CASE WHEN approved = 1 THEN 1 ELSE 0 END as approved
FROM BanRecords;
"""


def name():
    return 'tempban'


def description():
    return 'Ban a user from the server temporarily.'


async def _action(ctx, reply, user_id, duration, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return

    dur = parse_duration_str(duration)
    if dur is None:
        reply(ctx, 'Invalid duration: could not parse.', delete_after=15)
        return

    epoch_time = calendar.timegm(time.gmtime())
    needs_approval = True  # TODO: is always true

# TODO:
#    if cmm(member):
#        return await ctx.send("You cannot ban another staff member.")

    if dur - epoch_time <= 0:
        reply(ctx, 'Invalid duration: cannot be in the past.', delete_after=15)
        return

    with connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO ban_record (user_id, reason, moderator, unban_time, approved) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, ctx.author.id, dur, 0))
            connection.commit()
        # TODO: Consider adding this as an infraction as well.

    member = ctx.guild.get_member(user_id)
    try:
        await member.send(
            f'You have been banned from {ctx.guild.name} for a duration of {duration} and the following reason: {reason}'
            '\n\nIf you disagree with this decision, please feel free to reach out to an Administrator to appeal the ban.')
    except Forbidden:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...')
# TODO:
#   await ctx.guild.ban(member, reason=reason)
    await reply(ctx, f'{member.mention} has been banned from the server.')


#    await InfractionRecord.insertInfraction(member, ctx.author, 0,
#                                            f"{member.display_name} has been banned for a duration of "
#                                            f"{length} for \"{reason}\"",
#                                            ctx.guild.id)
#    if needs_approval:
#        embed = discord.Embed(title=f"Ban {ban_details[0][0]} Length Request",
#                              description=f"{ctx.author.name} would like to ban {member.name}for "
#                                          f"{length} for \"{reason}\"")
#        embed.set_thumbnail(url=f"{BASE_URL}/images/logo600.png")
#        embed.add_field(name="To Approve",
#                        value=f"/approve {ban_details[0][0]}", inline=True)
#        embed.add_field(name="To Change",
#                        value=f"/dispute {ban_details[0][0]} (time, Note: Time is from now, not original ban.)",
#                        inline=True)
#        embed.add_field(
#            name="To Deny", value=f"/deny {ban_details[0][0]}", inline=True)
#        await self.bot.get_guild(htb_guild).get_channel(ApprovalChannel).send(embed=embed)
#    await ctx.respond(
#        f"{member.display_name} has been banned for a duration of {length} for \"{reason}\"",
#        allowed_mentions=not_allowed_to_mention)

    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        duration: Option(str, 'Duration of the ban in human-friendly notation, e.g. 2mo for two months or 3w for three weeks.'),
        reason: Option(str, 'The note to add. Will be sent to the user in a DM as well.')
):
    await _action(ctx, Reply.slash, user_id, duration, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, duration: str, reason: str):
    await _action(ctx, Reply.prefix, user_id, duration, reason)


def setup(le_bot):
    le_bot.add_command(action_prefix)
