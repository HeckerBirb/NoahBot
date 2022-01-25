from discord.commands.context import ApplicationContext
from discord.ext import commands
from src.noahbot import bot

def name():
    return 'spoiler'

def description():
    return 'To report spoiler links'

@commands.dm_only()
async def perform_action(ctx: ApplicationContext, reply, link):

    if link is None:
        await reply(ctx, 'Please provide a link', send_followup=False)
        return

    else:
        await reply(ctx, 'Thank you for the report!', send_followup=False)
        await bot.get_channel(570672411067023372).send(f'{ctx.author.mention} has reported a spoiler link: {link}')
        return
    
