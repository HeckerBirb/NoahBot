from datetime import datetime
from typing import Optional, Dict, Union, List, cast

import aiohttp
import discord
from discord import Forbidden, Role

from src.cmds._proxy_helpers import perform_temp_ban
from src.conf import API_URL, HTB_API_SECRET, ChannelIDs, RoleIDs
from src.log4noah import STDOUT_LOG
from src.noahbot import bot


async def get_user_details(account_identifier) -> Optional[Dict]:
    acc_id_url = f'{API_URL}/discord/identifier/{account_identifier}?secret={HTB_API_SECRET}'

    async with aiohttp.ClientSession() as session:
        async with session.get(acc_id_url) as r:
            if r.status == 200:
                return await r.json()
            elif r.status == 404:
                STDOUT_LOG.error(f'Account identifier has been regenerated since last identification. Cannot re-verify.')
                return None
            else:
                STDOUT_LOG.error(f'Non-OK HTTP status code returned from identifier lookup: {r.status}.')
                return None


async def _check_for_ban(uid) -> Optional[Dict[str, Union[bool, str]]]:
    async with aiohttp.ClientSession() as session:
        token_url = f'{API_URL}/discord/{uid}/banned?secret={HTB_API_SECRET}'
        async with session.get(token_url) as r:
            if r.status == 200:
                ban_details = await r.json()
                return ban_details
            else:
                STDOUT_LOG.error(f"Could not fetch ban details for uid {uid}: non-OK status code returned ({r.status}). Body: {r.content}")
                return None


async def process_identification(ctx, reply, htb_user_details, user_id: int) -> Optional[List[Role]]:
    """
    Returns true if identification was successfully processed
    """
    htb_uid = htb_user_details['user_id']
    guild = bot.guilds[0]
    member = guild.get_member(user_id)
    banned_details = await _check_for_ban(htb_uid)

    # In an automated context, `ctx` is `None`, will need a refactor for autobans
    if ctx is not None and banned_details is not None and banned_details['banned']:
        # If user is banned, this field must be a string
        banned_until: str = cast(str, banned_details['ends_at'])[:10]  # Strip date e.g. from "2022-01-31T11:00:00.000000Z"
        banned_until_dt: datetime = datetime.strptime(banned_until, '%Y-%m-%d')
        ban_duration: str = f'{(banned_until_dt - datetime.now()).days}d'
        reason = 'Banned on the HTB Platform. Please contact HTB Support to appeal.'
        STDOUT_LOG.info(f'Discord user {member.name} ({member.id}) is platform banned. Banning from Discord...')
        await perform_temp_ban(bot, ctx, reply, member.id, ban_duration, reason, needs_approval=False, banned_by_bot=True, send_followup=True)

        embed = discord.Embed(
            title="Identification error",
            description=f"User {member.mention} ({member.id}) was platform banned HTB and thus also here.",
            color=0xff2429)
        await bot.get_channel(ChannelIDs.BOT_LOGS).send(embed=embed)
        return None

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
        pos_top = None
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

        if pos_top:
            STDOUT_LOG.debug(f'User is Hall of Fame rank {position}. Assigning role Top-{pos_top}...')
            to_assign.append(guild.get_role(RoleIDs.get_post_or_rank(pos_top)))
        else:
            STDOUT_LOG.debug(f'User is position {position}. No Hall of Fame roles for them.')
    if htb_user_details['machines']:
        to_assign.append(guild.get_role(RoleIDs.BOX_CREATOR))
    if htb_user_details['challenges']:
        to_assign.append(guild.get_role(RoleIDs.CHALLENGE_CREATOR))

    if member.nick != htb_user_details['user_name']:
        try:
            await member.edit(nick=htb_user_details['user_name'])
        except Forbidden as e:
            STDOUT_LOG.error(f'Exception whe trying to edit the nick-name of the user: {e}')

    # We don't need to remove any roles that are going to be assigned again
    to_remove = list(set(to_remove) - set(to_assign))
    if not to_remove:
        STDOUT_LOG.debug("No roles need to be removed")
    else:
        await member.remove_roles(*to_remove, atomic=True)

    await member.add_roles(*to_assign, atomic=True)
    return to_assign
