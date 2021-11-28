import discord
from discord.commands.context import ApplicationContext
from typing import Union


class Reply:
    """ Proxy for ctx.send and ctx.respond. Accepts same kwargs as the discord.InteractionResponse.send_message() does. """
    @staticmethod
    async def slash(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.respond(content=msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.send(content=msg, **kwargs)


def get_user_id(user_id: Union[str, discord.Member]):
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return None

    return user_id
