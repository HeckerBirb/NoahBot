from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply, remove_record
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.noahbot import bot


def name():
    return 'remove_infraction'


def description():
    return 'Remove a warning or a strike from a user by providing the infraction ID to remove.'


async def perform_action(ctx: ApplicationContext, reply, infraction_id):
    remove_record('DELETE FROM infraction_record WHERE id = %s', (infraction_id, ))
    await reply(ctx, f'Infraction record #{infraction_id} has been deleted.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.SR_MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, infraction_id: Option(str, 'ID of the infraction record to remove.')):  # type: ignore
    await perform_action(ctx, Reply.slash, infraction_id)


@commands.command(name=name(), help=description(), aliases=[name().replace('_', '')])
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_SR_MODERATORS))
async def action_prefix(ctx: ApplicationContext, infraction_id):
    await perform_action(ctx, Reply.prefix, infraction_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
