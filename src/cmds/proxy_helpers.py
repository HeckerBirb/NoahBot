import discord
from discord.commands.context import ApplicationContext
from typing import Union


class Reply:
    """ Proxy for ctx.send and ctx.respond. """
    @staticmethod
    async def slash(ctx, msg):
        await ctx.respond(msg)

    @staticmethod
    async def prefix(ctx, msg):
        await ctx.send(msg)


def get_user_id(user_id: Union[str, discord.Member]):
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return None

    return user_id
