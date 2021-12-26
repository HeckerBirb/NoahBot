from discord.errors import Forbidden, HTTPException
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply, get_user_id

"""
CREATE TABLE IF NOT EXISTS `infraction_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` mediumtext NOT NULL,
  `weight` int(11) NOT NULL,
  `moderator` varchar(18) NOT NULL,
  `date` DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE `infraction_record`;

INSERT INTO infraction_record
SELECT
    id, member, reason, strikes, moderator, date
FROM hotbot.Strikes;
"""


def name():
    return 'strike'


def description():
    return 'Strike the user with the selected weight. DMs the user about the strike and the reason why.'


async def perform_action(ctx: ApplicationContext, reply, user_id, weight, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return
    member = bot.guilds[0].get_member(user_id)

    if len(reason) == 0:
        reply(ctx, 'The reason is empty. Try again...')
        return

    moderator = ctx.author.id
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO infraction_record (user_id, reason, weight, moderator) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, reason, weight, moderator))
            connection.commit()

    await reply(ctx, f'{member.mention} has been warned with a strike weight of {weight}.')

    try:
        await member.send(
            f'You have been warned on {bot.guilds[0].name} with a strike value of {weight}. After a total value of 3, permanent exclusion from the server may be enforced.\n'
            f'Following is the reason given:\n>>> {reason}\n')
    except Forbidden:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to ban them...')
    except HTTPException:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.")
        return


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        weight: Option(str, 'Weight of the strike: 1 = hard slap on the wrist, 3 = final warning; consider banning.'),
        reason: Option(str, 'Strike reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, weight, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, weight: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, weight, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
