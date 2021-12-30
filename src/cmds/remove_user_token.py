from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply, remove_record, get_user_id
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.noahbot import bot


def name():
    return 'remove_user_token'


def description():
    return 'Remove all records of identification the user has made from the database.'


async def perform_action(ctx: ApplicationContext, reply, user_id):
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.', send_followup=False)
        return

    remove_record('DELETE FROM htb_discord_link WHERE discord_user_id = %s or htb_user_id = %s', (user_id, user_id))
    await reply(ctx, f'All tokens related to Discord or HTB ID "{user_id}" have been deleted.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'ID of the Discord or HTB user for which all identification records should be removed.')):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description(), aliases=[name().replace('_', '')])
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
