import random
from typing import List

from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, ROOT_DIR
from src.cmds._proxy_helpers import Reply, get_user_id
from discord.errors import Forbidden

baby_names: List


def name():
    return 'badname'


def description():
    return 'Changes the nickname of a user to ChangeMe.'


async def perform_action(ctx: ApplicationContext, reply, user_id: str):
    global baby_names

    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return

    member = ctx.guild.get_member(int(user_id))
    if member is None:
        member = await bot.fetch_user(user_id)

    new_name = random.choice(baby_names) + ' McVerify'

    try:
        await member.edit(nick=new_name)
    except Forbidden:
        await reply(ctx, f'Cannot rename {member.mention}. Am I even allowed to?')
        return

    try:
        await member.send(
            'Greetings! It has been determined by a member of the staff team that your nickname '
            'was breaking the rules. As a result your nickname has been randomized. Please verify your '
            'HTB account (see #welcome for how) to have your name reset to your HTB username.'
        )
    except Forbidden:
        await reply(ctx, f'Cannot DM user {member.mention}. Perhaps they do not allow DMs from strangers?')
        return

    await reply(ctx, f"{member.name}'s name has been updated to {new_name}")


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    global baby_names
    with open(ROOT_DIR / 'resources' / 'unisex_baby_names.txt') as r:
        baby_names = [baby_name for baby_name in r.read().split('\n')]
    le_bot.add_command(action_prefix)
