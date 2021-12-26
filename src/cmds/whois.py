from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.commands import Option
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE
from src.cmds._proxy_helpers import Reply, get_user_id
from mysql.connector import connect


def name():
    return 'whois'


def description():
    return 'Given a Discord user ID, show the associated HTB user ID and vise versa.'


async def _whois(ctx: ApplicationContext, user_id, reply):
    identification = dict()
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT discord_user_id, htb_user_id FROM htb_discord_link WHERE discord_user_id = %s or htb_user_id = %s LIMIT 1"""
            cursor.execute(query_str, (user_id, user_id))
            for row in cursor.fetchall():
                identification['discord_id'] = row[0]
                identification['htb_id'] = row[1]

    if len(identification) == 0:
        await reply(ctx, 'I cannot find that ID in our records.')
        return

    mention = bot.guilds[0].get_member(int(identification['discord_id']))
    msg = f"""**{mention}**
Discord ID: {identification['discord_id']}
HTB profile: <https://app.hackthebox.com/users/{identification['htb_id']}>"""
    await reply(ctx, msg)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def whois_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await _whois(ctx, user_id, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def whois_prefix(ctx: ApplicationContext, user_id):
    await _whois(ctx, user_id, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(whois_prefix)
