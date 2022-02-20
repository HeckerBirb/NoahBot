import discord
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands
from mysql.connector import connect

from src.cmds._proxy_helpers import Reply, get_user_id
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE
from src.noahbot import bot


def name():
    return 'whois'


def description():
    return 'Given a Discord user ID, show the associated HTB user ID and vise versa.'


async def _whois(ctx: ApplicationContext, user_id, reply):
    identification = dict()
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT discord_user_id, htb_user_id FROM htb_discord_link WHERE discord_user_id = %s or htb_user_id = %s LIMIT 1"""
            cursor.execute(query_str, (user_id, user_id))
            for row in cursor.fetchall():
                identification['discord_id'] = row[0]
                identification['htb_id'] = row[1]

    if len(identification) == 0:
        await reply(ctx, 'I cannot find that ID in our records.', send_followup=False)
        return

    user = await bot.fetch_user(int(identification['discord_id']))

    embed = discord.Embed(title=" ", color=0xb98700)
    if user.avatar is not None:
        embed.set_author(name=user, icon_url=user.avatar)
        embed.set_thumbnail(url=user.avatar)
    else:
        embed.set_author(name=user)
    embed.add_field(name="Username:", value=user, inline=True)
    embed.add_field(name="Discord ID:", value=user.id, inline=True)
    embed.add_field(name="HTB Profile:", value=f"<https://www.hackthebox.com/home/users/profile/{identification['htb_id']}>", inline=False)
    embed.set_footer(text=f"More info: ++history {user.id}")
    await reply(ctx, embed=embed, send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR, SlashPerms.HTB_STAFF], name=name(), description=description())
async def whois_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await _whois(ctx, user_id, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS + PrefixPerms.ALL_HTB_STAFF))
async def whois_prefix(ctx: ApplicationContext, user_id):
    await _whois(ctx, user_id, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(whois_prefix)
