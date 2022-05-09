import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply
from src.conf import ChannelIDs, GUILD_ID
from src.noahbot import bot

async def get_user_cert(name, certid) -> Optional[Dict]:
    acc_id_url = f'{API_URL}/certificate/lookup/?id={certid}&name={name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(acc_id_url) as r:
            if r.status == 200:
                return await r.json()
            elif r.status == 404:
                STDOUT_LOG.error(f'Account identifier has been regenerated since last identification. Cannot re-verify.')
                return None
            else:
                STDOUT_LOG.error(f'Non-OK HTTP status code returned from identifier lookup: {r.status}.')
                return None
def name():
    return 'validate'


def description():
    return 'Validate your HTB Certification!'


async def perform_action(ctx: ApplicationContext, reply, name: str, certid: str):
    if not name or not certid:
        await reply("Please provide your name and certid")
    self.get_user_cert(name, certid)

@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, name: str):
    await perform_action(ctx, Reply.slash, name, certid)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext, name: Option(str, 'Your Name on your Certification', certid: Option(str, 'Your Certificate ID'))):
    await perform_action(ctx, Reply.prefix, name, certid)


def setup(le_bot):
    le_bot.add_command(action_prefix)