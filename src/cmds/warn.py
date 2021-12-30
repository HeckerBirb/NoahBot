from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply, perform_infraction_record


def name():
    return 'warn'


def description():
    return 'Warns a user of an action. Adds no weight but DMs the user about the warning and the reason why.'


async def perform_action(ctx: ApplicationContext, reply, user_id, reason):
    await perform_infraction_record(ctx, reply, bot.guilds[0], user_id, 0, reason)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        reason: Option(str, 'Strike reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
