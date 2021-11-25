import discord
from discord.ext import commands
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_URI, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE
from src.cmds.proxy_helpers import Reply
import mysql.connector


def description():
    return 'Given a Discord user ID, show the associated HTB user ID and vise versa.'


def name():
    return 'whois'


async def _whois(ctx, user_id, reply):
    identification = dict()
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return

    with mysql.connector.connect(host=MYSQL_URI, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT * FROM token WHERE user = %s or htbuser = %s LIMIT 1"""
            cursor.execute(query_str, (user_id, user_id))
            for row in cursor.fetchall():
                # row = id, is_token_valid, discord_id, htb_id
                identification['discord_id'] = row[2]
                identification['htb_id'] = row[3]

    if len(identification) == 0:
        await reply(ctx, 'I cannot find that ID in our records.')
        return

    mention = ctx.guild.get_member(int(identification['discord_id']))
    msg = f"""**{mention}**
Discord ID: {identification['discord_id']}
HTB ID: {identification['htb_id']}"""
    await reply(ctx, msg)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def whois_slash(ctx, user_id):
    await _whois(ctx, user_id, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def whois_prefix(ctx, user_id):
    await _whois(ctx, user_id, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(whois_prefix)
