from typing import Union

from discord import TextChannel
from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.noahbot import bot


def name():
    return 'slowmode'


def description():
    return 'Add slow mode to the channel. Specifying a value of 0 removes the slow mode again.'


async def perform_action(ctx: ApplicationContext, reply, channel: Union[int, TextChannel], seconds):
    """Sets a slowmode on a channel"""
    if isinstance(channel, str):
        try:
            channel_id = int(channel.replace('<#', '').replace('>', ''))
            channel = bot.guilds[0].get_channel_or_thread(channel_id)
        except ValueError:
            await reply(ctx, f"""I don't know what "{channel.mention}" is. Please use #channel-reference or a channel ID.""", send_followup=False)
            return

    try:
        seconds = int(seconds)
    except ValueError:
        await reply(ctx, f'Malformed amount of seconds: {seconds}.')
        return

    if seconds < 0:
        seconds = 0
    if seconds > 30:
        seconds = 30
    await channel.edit(slowmode_delay=seconds)
    await reply(ctx, f'Slowmode set in {channel.name} to {seconds} seconds.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        channel: Option(TextChannel, 'Channel to enable slowmode on.'),
        seconds: Option(int, 'Amount of seconds to set slowmode as so that 0 < x < 30.')
):
    await perform_action(ctx, Reply.slash, channel, seconds)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, channel, seconds):
    await perform_action(ctx, Reply.prefix, channel, seconds)


def setup(le_bot):
    le_bot.add_command(action_prefix)
