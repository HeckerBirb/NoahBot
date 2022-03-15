import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply
from src.conf import ChannelIDs, GUILD_ID
from src.noahbot import bot


def name():
    return 'spoiler'


def description():
    return 'Add the URL which has spoiler link'


async def perform_action(ctx: ApplicationContext, reply, url: str):
    if len(url) == 0:
        await ctx.send('Please provide the spoiler URL.')
        return

    if ctx.guild and reply == Reply.prefix:
        await ctx.message.delete()

    embed = discord.Embed(title="Spoiler Report", color=0xb98700)
    embed.add_field(name=f"{ctx.author} has submitted a spoiler.", value=f"URL: <{url}>", inline=False)

    await bot.get_channel(ChannelIDs.SPOILER_CHAN).send(embed=embed)
    await reply(ctx, "Thanks for the reporting the spoiler", ephemeral=True, delete_after=15)


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, url: str):
    await perform_action(ctx, Reply.slash, url)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, url: str):
    await perform_action(ctx, Reply.prefix, url)


def setup(le_bot):
    le_bot.add_command(action_prefix)