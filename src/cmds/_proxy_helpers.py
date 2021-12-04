import calendar
import re
import time

import discord
from discord.commands.context import ApplicationContext
from typing import Union, Optional


class Reply:
    """ Proxy for ctx.send and ctx.respond. Accepts same kwargs as the discord.InteractionResponse.send_message() does. """
    @staticmethod
    async def slash(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.respond(content=msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, **kwargs):
        await ctx.send(content=msg, **kwargs)


def get_user_id(user_id: Union[str, discord.Member]) -> Optional[int]:
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return None

    return user_id


def parse_duration_str(duration: str) -> Optional[int]:
    dur = re.compile(r'(-?(?:\d+\.?\d*|\d*\.?\d+)(?:e[-+]?\d+)?)\s*([a-z]*)', re.IGNORECASE)
    units = {'s': 1}
    units['m'] = units['s'] * 60
    units['h'] = units['hr'] = units['m'] * 60
    units['d'] = units['day'] = units['h'] * 24
    units['wk'] = units['w'] = units['d'] * 7
    units['month'] = units['months'] = units['mo'] = units['d'] * 30
    units['y'] = units['yr'] = units['d'] * 365
    sum_seconds = 0

    while duration:
        m = dur.match(duration)
        if not m:
            return None
        duration = duration[m.end():]
        sum_seconds += int(m.groups()[0]) * units.get(m.groups()[1], 1)

    epoch_time = calendar.timegm(time.gmtime())
    return epoch_time + sum_seconds
