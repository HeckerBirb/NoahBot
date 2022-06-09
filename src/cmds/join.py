from typing import cast

import discord
from discord import Role
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply
from src.conf import GUILD_ID, JOINABLE_ROLES
from src.noahbot import bot


def name():
    return 'join'


def description():
    return 'Join a vanity role if such is specified, otherwise list the vanity roles available to join.'


async def perform_action(ctx: ApplicationContext, reply, role_name):
    if not ctx.guild:
        await reply(ctx, 'This command cannot be used in a DM.', send_followup=False)
        return

    # No role or empty role name passed
    if not role_name or role_name.isspace():
        embed = discord.Embed(title=" ", color=0x3d85c6)
        embed.set_author(name="Joinable Roles")
        embed.set_footer(text="Use the command ++join <role> to join a role.")
        for role, value in JOINABLE_ROLES.items():
            embed.add_field(name=role, value=value[1], inline=True)
        return await reply(ctx, embed=embed, send_followup=False)

    filtered = [(k, v) for k, v in JOINABLE_ROLES.items() if role_name.lower() in k.lower()]
    if not filtered:
        return await reply(ctx, "I don't know what role that is. Did you spell it right?", send_followup=False, ephemeral=True)
    if len(filtered) > 1:
        return await reply(ctx, "Matched multiple roles, try being more specific", send_followup=False, ephemeral=True)
    _, details = filtered[0]
    rid, _ = details
    guild_role = ctx.guild.get_role(rid)
    await ctx.author.add_roles(guild_role)
    await reply(ctx, f'Welcome to {guild_role.name}!', send_followup=False, ephemeral=True)


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, role_name: Option(str, 'The name of the role you want to join.')):  # type: ignore
    await perform_action(ctx, Reply.slash, role_name)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, *role_name):
    await perform_action(ctx, Reply.prefix, ' '.join(role_name))


def setup(le_bot):
    le_bot.add_command(action_prefix)
