from datetime import datetime

from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands
from mysql.connector import connect

from src.cmds._proxy_helpers import Reply, get_user_id
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.noahbot import bot

"""
CREATE TABLE IF NOT EXISTS `user_note` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `note` text NOT NULL,
  `date` date NOT NULL,
  `moderator` varchar(18) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE `user_note`;

INSERT INTO `user_note`
SELECT
    id, member, note, date, moderator
FROM hotbot.Notes;
"""


def name():
    return 'addnote'


def description():
    return 'Add a note to the users history records. Only intended for staff convenience.'


async def perform_action(ctx: ApplicationContext, reply, user_id, note):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return

    if len(note) == 0:
        await reply(ctx, 'The note is empty. Try again...', send_followup=False)
        return

    moderator = ctx.author.id
    today = datetime.date(datetime.now())
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO user_note (user_id, note, date, moderator) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query_str, (user_id, note, today, moderator))
            connection.commit()

    await reply(ctx, 'Note added.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.'), note: Option(str, 'The note to add.')):  # type: ignore
    await perform_action(ctx, Reply.slash, user_id, note)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id, *note):
    await perform_action(ctx, Reply.prefix, user_id, ' '.join(note))


def setup(le_bot):
    le_bot.add_command(action_prefix)
