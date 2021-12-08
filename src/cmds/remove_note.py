from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply, remove_record


def name():
    return 'remove_note'


def description():
    return 'Remove a note from a user by providing the note ID to remove.'


async def perform_action(ctx: ApplicationContext, reply, note_id):
    remove_record('DELETE FROM user_note WHERE id = %s', (note_id,))
    await reply(ctx, f'Infraction record #{note_id} has been deleted.')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, note_id: Option(str, 'ID of the note record to remove.')):
    await perform_action(ctx, Reply.slash, note_id)


@commands.command(name=name(), help=description(), aliases=[name().replace('_', '')])
@commands.has_any_role(*PrefixPerms.ALL_ADMINS)
async def action_prefix(ctx: ApplicationContext, note_id):
    await perform_action(ctx, Reply.prefix, note_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
