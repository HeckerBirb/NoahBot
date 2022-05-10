from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from log4noah import STDOUT_LOG
from src.cmds._proxy_helpers import Reply
from src.conf import GUILD_ID, JOINABLE_ROLES
from src.noahbot import bot


def name():
    return 'leave'


def description():
    return 'Removes the vanity role from your user.'


async def perform_action(ctx: ApplicationContext, reply, role_name):
    if not ctx.guild:
        await reply(ctx, 'This command cannot be used in a DM.', send_followup=False)
        return

    for role in JOINABLE_ROLES.keys():
        if role_name.lower() in role.lower():
            r = JOINABLE_ROLES.get(role)
            if r:
                role_id = r[0]
                break
    else:
        return await reply(ctx, "I don't know what role that is. Did you spell it right?", send_followup=False)

    the_role = ctx.guild.get_role(role_id)
    await ctx.author.remove_roles(the_role)
    await reply(ctx, f'You have left {the_role.name}.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, role_name: Option(str, 'The name of the role you want to leave.')):  # type: ignore
    await perform_action(ctx, Reply.slash, role_name)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, *role_name):
    await perform_action(ctx, Reply.prefix, ' '.join(role_name))


def setup(le_bot):
    le_bot.add_command(action_prefix)
