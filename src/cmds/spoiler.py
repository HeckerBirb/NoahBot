from typing import Union
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, ChannelIDs,GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'spoiler'

def description():
    return 'Add the URL which has spoiler link'

async def perform_action(ctx: ApplicationContext, reply, url: str):
    if len(url) == 0:
        await ctx.send('Please provide the spoiler URL.')
        return
    
    ctx.message.delete()
    embed = discord.Embed(title="Error: Spoiler Report.", color=0xFF0000)
    await bot.get_channel(ChannelIDs.BOT_LOGS).send(embed=embed(ctx, f"{ctx.author.mention} has submitted a spoiler report"+ url))
    await reply(ctx, "Thanks for the reporting the spoiler")


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, reply, url: str):
    await perform_action(ctx, reply, url)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, url: str):
    await perform_action(ctx, Reply.prefix, url)



def setup():
    le_bot = bot.add_command(perform_action)