from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import GUILD_ID, JOINABLE_ROLES
from src.cmds._proxy_helpers import Reply


def name():
    return 'leave'


def description():
    return 'Removes the vanity role from your user.'


async def perform_action(ctx: ApplicationContext, reply, role_name):
    if not ctx.guild:
        reply(ctx, 'This command cannot be used in a DM.')
        return

    role_id = None
    for role in JOINABLE_ROLES.keys():
        if role_name.lower() in role.lower():
            role_id = JOINABLE_ROLES.get(role)

    if role_id is None:
        await reply(ctx, "I don't know what role that is. Did you spell it right?")
        return

    the_role = ctx.guild.get_role(role_id)
    await ctx.author.remove_roles(the_role)
    await reply(ctx, f'You have left {the_role.name}.')


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, role_name: Option(str, 'The name of the role you want to join.')):
    await perform_action(ctx, Reply.slash, role_name)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, *role_name):
    await perform_action(ctx, Reply.prefix, ' '.join(role_name))


def setup(le_bot):
    le_bot.add_command(action_prefix)
