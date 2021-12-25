from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply


def name():
    return 'approve'


def description():
    return 'Approve a ban request.'


async def perform_action(ctx: ApplicationContext, reply, ban_id):
    with connect(host=MYSQL_HOST, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """UPDATE ban_record SET approved = 1 WHERE id = %s"""
            cursor.execute(query_str, (ban_id, ))
            connection.commit()
    await reply(ctx, f'Ban approval has been recorded.')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, ban_id: Option(int, 'ID of the ban record')):
    await perform_action(ctx, Reply.slash, ban_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, ban_id):
    await perform_action(ctx, Reply.prefix, ban_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
