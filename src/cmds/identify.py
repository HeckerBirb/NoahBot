import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union, Optional

import aiohttp
import discord
from discord.errors import Forbidden
from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.commands import Option
from mysql.connector import connect

from src.cmds._error_handling import interruptable
from src.log4noah import STDOUT_LOG
from src.noahbot import bot
from src.conf import GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, ChannelIDs, \
    HTB_API_SECRET, API_URL, RoleIDs
from src.cmds._proxy_helpers import Reply, perform_temp_ban

"""
CREATE TABLE IF NOT EXISTS `htb_discord_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_identifier` varchar(255) NOT NULL,
  `discord_user_id` varchar(42) NOT NULL,
  `htb_user_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE `htb_discord_link`;

INSERT INTO `htb_discord_link`
SELECT
    id, token, user, htbuser
FROM hotbot.token;
"""


@dataclass
class HtbDiscordLink:
    acc_id: int
    dis_user_id: int
    htb_user_id: int


@dataclass
class NaughtyList:
    known_token_belongs_to_different_discord_user: bool = False
    htb_user_from_lookup_resolves_to_different_discord_user: bool = False
    discord_user_resolves_to_different_htb_user: bool = False


def name():
    return 'identify'


def description():
    return 'Identify yourself on the HTB Discord server by linking your HTB account ID to your Discord user ID.'


async def remove_their_message(ctx: ApplicationContext, reply):
    if ctx.guild and reply == Reply.prefix:
        await ctx.message.delete()


async def perform_action(ctx: ApplicationContext, reply, account_identifier):
    await remove_their_message(ctx, reply)
    if len(account_identifier) != 60:
        await reply(ctx, "This Account Identifier does not appear to be the right length (must be 60 characters long).", ephemeral=True)
        return

    await reply(ctx, 'Identification initiated, please wait...', ephemeral=True)
    acc_id_url = f'{API_URL}/discord/identifier/{account_identifier}?secret={HTB_API_SECRET}'

    async with aiohttp.ClientSession() as session:
        async with session.get(acc_id_url) as r:
            if r.status == 200:
                htb_user_details = await r.json()
            else:
                # TODO: figure out HTTP error code if invalid id and handle default case + that case
                embed = discord.Embed(title="Error: Invalid account identifier.", color=0xFF0000)
                await reply(ctx, embed=embed, ephemeral=True, send_followup=True)
                return

    json_htb_user_id = htb_user_details['user_id']
    naughty_list = NaughtyList()

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with interruptable(connection.cursor()) as cursor:

            # Step 1: Check if the Account Identifier has already been recorded and if they are the previous owner.
            # Scenario:
            #   - I create a new Discord account.
            #   - I reuse my previous Account Identifier.
            #   - I now have an "alt account" with the same roles.
            most_recent_rec = None
            query_str = """SELECT * FROM htb_discord_link WHERE account_identifier = %s ORDER BY id DESC LIMIT 1"""
            cursor.execute(query_str, (account_identifier, ))
            for row in cursor.fetchall():
                # row = id, account_identifier, discord_user_id, htb_user_id
                most_recent_rec = HtbDiscordLink(acc_id=row[1], dis_user_id=int(row[2]), htb_user_id=int(row[3]))

            if most_recent_rec is not None:
                if most_recent_rec.dis_user_id != ctx.author.id:
                    naughty_list.known_token_belongs_to_different_discord_user = True
                    raise interruptable.Interrupt

            # Step 2: Given the htb_user_id from JSON, check if each discord_user_id are different than ctx.author.id.
            # Scenario:
            #   - I have a Discord account that is linked already to a "Hacker" role.
            #   - I create a new HTB account.
            #   - I identify with the new account.
            #   - `SELECT * FROM htb_discord_link WHERE htb_user_id = %s` will be empty because the new account has not been verified before. All is good.
            #   - I am now "Noob" rank.
            user_links = []
            query_str = """SELECT * FROM htb_discord_link WHERE htb_user_id = %s"""
            cursor.execute(query_str, (json_htb_user_id, ))
            for row in cursor.fetchall():
                # row = id, account_identifier, discord_user_id, htb_user_id
                user_links.append(HtbDiscordLink(acc_id=row[1], dis_user_id=int(row[2]), htb_user_id=int(row[3])))

            for u_link in user_links:
                if ctx.author.id != u_link.dis_user_id:
                    naughty_list.htb_user_from_lookup_resolves_to_different_discord_user = True
                    orig_discord_id = u_link.dis_user_id
                    raise interruptable.Interrupt

            # Step 3: Check if discord_user_id already has a link to an htb_user_id, and if JSON/db HTB IDs are the same.
            # Scenario:
            #   - I have a new, unlinked Discord account.
            #   - Clubby generates a new token and gives it to me.
            #   - `SELECT * FROM htb_discord_link WHERE discord_user_id = %s` will be empty because I have not identified before.
            #   - I am now Clubby.
            user_links = []
            query_str = """SELECT * FROM htb_discord_link WHERE discord_user_id = %s"""
            cursor.execute(query_str, (ctx.author.id, ))
            for row in cursor.fetchall():
                # row = id, account_identifier, discord_user_id, htb_user_id
                user_links.append(HtbDiscordLink(acc_id=row[1], dis_user_id=int(row[2]), htb_user_id=int(row[3])))

            for u_link in user_links:
                if u_link.htb_user_id != json_htb_user_id:
                    naughty_list.discord_user_resolves_to_different_htb_user = True
                    orig_htb_id = u_link.htb_user_id

        if any(naughty_list.__dict__.values()):
            if naughty_list.known_token_belongs_to_different_discord_user:
                error_desc=f'Verified user {ctx.author.mention} tried to identify as another identified user.\n' \
                           f'Discord UID: {most_recent_rec.dis_user_id}, HTB UID: {most_recent_rec.htb_user_id}'

            elif naughty_list.htb_user_from_lookup_resolves_to_different_discord_user:
                error_desc=f'The HTB account {json_htb_user_id} was attempted identified by user <@{ctx.author.id}>, but is tied to another Discord account.\n' \
                           f'Original Discord UID: <@{orig_discord_id}>, shared HTB UID: {json_htb_user_id}).'

            elif naughty_list.discord_user_resolves_to_different_htb_user:
                error_desc=f'User {ctx.author.mention} (Discord UID {ctx.author.id}) tried to verify with a different HTB account.\n' \
                           f'Original HTB UID: {orig_htb_id}, new HTB UID: {json_htb_user_id}.'

            else:
                error_desc = f'Case not supported. NaughtyList checks: {naughty_list}'

            embed = discord.Embed(title='Identification error', description=error_desc, color=0xff2429)
            await bot.get_channel(ChannelIDs.BOT_LOGS).send(embed=embed)

            await reply(ctx, 'Identification error: please contact an online Moderator or Administrator for help.', ephemeral=True, send_followup=True)
            return

        with connection.cursor() as cursor:
            query_str = """INSERT INTO htb_discord_link (account_identifier, discord_user_id, htb_user_id) VALUES (%s, %s, %s)"""
            cursor.execute(query_str, (account_identifier, ctx.author.id, json_htb_user_id))
            connection.commit()

    await process_identification(ctx, reply, htb_user_details, ctx.author.id)

    member = bot.guilds[0].get_member(ctx.author.id)
    try:
        await member.edit(nick=htb_user_details['user_name'])
    except Forbidden as e:
        # TODO Fix this
        raise e

    await reply(ctx, f'Your Discord user has been successfully identified as HTB user {json_htb_user_id}.', ephemeral=True, send_followup=True)


async def _check_for_ban(uid) -> Optional[Dict[str, Union[bool, str]]]:
    async with aiohttp.ClientSession() as session:
        token_url = f'{API_URL}/discord/{uid}/banned?secret={HTB_API_SECRET}'
        async with session.get(token_url) as r:
            if r.status == 200:
                ban_details = await r.json()
                return ban_details
            else:
                # TODO: Error log
                STDOUT_LOG.error(f"Could not fetch ban details for uid {uid}.")
                return None


async def process_identification(ctx, reply, htb_user_details, user_id: int):
    htb_uid = htb_user_details['user_id']
    guild = bot.guilds[0]
    member = guild.get_member(user_id)
    banned_details = await _check_for_ban(htb_uid)

    if banned_details is not None and banned_details['banned']:
        banned_until: str = banned_details['ends_at'][:10]  # Strip date e.g. from "2022-01-31T11:00:00.000000Z"
        banned_until: datetime = datetime.strptime(banned_until, '%Y-%m-%d')
        ban_duration: str = f'{(banned_until - datetime.now()).days}d'
        reason = 'Banned on the HTB Platform. Please contact HTB Support to appeal.'
        STDOUT_LOG.info(f'Discord user {member.name} ({member.id}) is platform banned. Banning from Discord...')
        await perform_temp_ban(bot, ctx, reply, member.id, ban_duration, reason, needs_approval=False, banned_by_bot=True)

        embed = discord.Embed(
            title="Identification error",
            description=f"User {member.mention} was platform banned HTB and thus also here.",
            color=0xff2429)
        await bot.get_channel(ChannelIDs.BOT_LOGS).send(embed=embed)
        return

    to_remove = []

    for role in member.roles:
        if role.id in RoleIDs.ALL_RANKS + RoleIDs.ALL_POSITIONS:
            to_remove.append(guild.get_role(role.id))

    to_assign = [guild.get_role(RoleIDs.get_post_or_rank(htb_user_details['rank']))]

    if htb_user_details['vip']:
        to_assign.append(guild.get_role(RoleIDs.VIP))
    if htb_user_details['dedivip']:
        to_assign.append(guild.get_role(RoleIDs.VIP_PLUS))
    if htb_user_details['hof_position'] != "unranked":
        position = int(htb_user_details['hof_position'])
        if position == 1:
            pos_top = '1'
        elif position <= 5:
            pos_top = '5'
        elif position <= 10:
            pos_top = '10'
        elif position <= 25:
            pos_top = '25'
        elif position <= 50:
            pos_top = '50'
        elif position <= 100:
            pos_top = '100'
        else:
            pos_top = position
        if int(pos_top) <= 100:
            STDOUT_LOG.debug(f'User is Hall of Fame rank {position}. Assigning role Top-{pos_top}...')
            to_assign.append(guild.get_role(RoleIDs.get_post_or_rank(pos_top)))
        else:
            STDOUT_LOG.debug(f'User is position {position}. No Hall of Fame roles for them. :)')
    if htb_user_details['machines']:
        to_assign.append(guild.get_role(RoleIDs.BOX_CREATOR))
    if htb_user_details['challenges']:
        to_assign.append(guild.get_role(RoleIDs.CHALLENGE_CREATOR))
    if set(to_remove) == set(to_assign):
        STDOUT_LOG.debug("Roles to Remove and Assign are the same; Doing nothing.")
        return
    else:
        await member.remove_roles(*to_remove, atomic=True)
        await member.add_roles(*to_assign, atomic=True)
    return to_assign


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, account_identifier: Option(str, 'The Account Identifier from your HTB Platform profile page.')):
    await perform_action(ctx, Reply.slash, account_identifier)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, account_identifier):
    await perform_action(ctx, Reply.prefix, account_identifier)


def setup(le_bot):
    le_bot.add_command(action_prefix)
