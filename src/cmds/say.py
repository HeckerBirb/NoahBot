from typing import Union

import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds.proxy_helpers import Reply


def name():
    return 'say'


def description():
    return 'Send a message as the bot in the specified channel.'


async def perform_action(ctx: ApplicationContext, reply, channel: Union[int, discord.TextChannel], message: str):
    if isinstance(channel, str):
        try:
            channel_id = int(channel.replace('<#', '').replace('>', ''))
            channel = ctx.guild.get_channel_or_thread(channel_id)
            await channel.send(message)
        except ValueError:
            await reply(ctx, 'Error: channel must be a #channel-reference or a channel ID as digits.')
        return

    await channel.send(message)
    await reply(ctx, f'Message sent to {channel.mention}.')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        channel: Option(discord.TextChannel, 'Channel to send the message to.'),
        message: Option(str, 'Message to send as the bot.')
):
    await perform_action(ctx, Reply.slash, channel, message)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, channel, message):
    await perform_action(ctx, Reply.prefix, channel, message)


def setup(le_bot):
    le_bot.add_command(action_prefix)
