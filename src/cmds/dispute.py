from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'dispute'


def description():
    return 'Dispute a ban request by changing the ban duration, then approve it.'


async def perform_action(ctx: ApplicationContext, reply, ban_id, duration):
    # TODO: should also set "approved" to 1
    # TODO: when calculating the new "unban time", use `timestamp` from DB as baseline
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        ban_id: Option(int, 'Ban ID from ban request.'),
        duration: Option(str, 'New duration of the temporary ban, from the point in time of the ban.')
):
    await perform_action(ctx, Reply.slash, ban_id, duration)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, ban_id, duration):
    await perform_action(ctx, Reply.prefix, ban_id, duration)


def setup(le_bot):
    le_bot.add_command(action_prefix)
