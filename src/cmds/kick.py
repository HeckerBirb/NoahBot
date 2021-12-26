from discord.errors import Forbidden, HTTPException
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms
from src.cmds._proxy_helpers import Reply, get_user_id


def name():
    return 'kick'


def description():
    return 'Kick a user from the server.'


async def perform_action(ctx: ApplicationContext, reply, user_id, reason):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return
    member = ctx.guild.get_member(user_id)

    if len(reason) == 0:
        reason = 'No reason given...'

    try:
        await member.send(
            f'You have been kicked from {ctx.guild.name} for the following reason:\n>>> {reason}\n')
    except Forbidden:
        await reply(ctx, 'Could not DM member due to privacy settings, however will still attempt to kick them...')
    except HTTPException:
        await reply(ctx, "Here's a 400 Bad Request for you. Just like when you tried to ask me out, last week.")
        return

    await ctx.guild.kick(user=member, reason=reason)
    await reply(ctx, f'{member.name} got the boot!')


@bot.slash_command(permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        reason: Option(str, 'Kick reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id, *reason):
    await perform_action(ctx, Reply.prefix, user_id, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
