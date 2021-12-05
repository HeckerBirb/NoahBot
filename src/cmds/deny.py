from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.cmds import unban
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_URI, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply


def name():
    return 'deny'


def description():
    return 'Deny a ban request and unban the member.'


async def perform_action(ctx: ApplicationContext, reply, ban_id):
    with connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            user_id = (-1)
            query_str = 'SELECT user_id FROM ban_record WHERE id = %s'
            cursor.execute(query_str, (ban_id, ))

            for row in cursor.fetchall():
                user_id = row[0]

            await unban.perform_action(ctx, reply, user_id)
            query_str = 'DELETE FROM ban_record WHERE id = %s'
            cursor.execute(query_str, (ban_id,))
            connection.commit()


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, ban_id: Option(int, 'Ban ID from ban request.')):
    await perform_action(ctx, Reply.slash, ban_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, ban_id):
    await perform_action(ctx, Reply.prefix, ban_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
