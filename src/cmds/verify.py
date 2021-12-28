import discord
from discord.errors import Forbidden, HTTPException
from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'verify'


def description():
    return 'Receive instructions in a DM on how to identify yourself with your HTB account.'


async def perform_action(ctx: ApplicationContext, reply):
    if ctx.guild:
        await reply(ctx, 'Please see your DMs for instructions on how to verify your HTB account.')
    else:
        await reply(ctx, 'Please follow the below instructions on how to verify your HTB account.')

    member = ctx.author

    # Step one
    embed_step1 = discord.Embed(color=0x9ACC14)
    embed_step1.add_field(
        name='Step 1: Log in at Hack The Box',
        value='Log in to your Hack The Box account at <https://www.hackthebox.com/> and navigate to the settings page.',
        inline=False)
    embed_step1.set_image(url='https://media.discordapp.net/attachments/724587782755844098/839871275627315250/unknown.png')

    # Step two
    embed_step2 = discord.Embed(color=0x9ACC14)
    embed_step2.add_field(
        name='Step 2: Locate the Account Identifier',
        value='In the settings tab, look for a field called "Account Identifier". Next, click the green button to copy your secret identifier.',
        inline=False)
    embed_step2.set_image(url='https://media.discordapp.net/attachments/724587782755844098/839871332963188766/unknown.png')

    # Step three
    embed_step3 = discord.Embed(color=0x9ACC14)
    embed_step3.add_field(
        name='Step 3: Identification',
        value='Now either reply in here with `++identify IDENTIFIER_HERE` substituting `IDENTIFIER_HERE` with your secret Account Identifier, '
              'or alternatively type `/identify IDENTIFIER_HERE` in the bot-commands channel.\n\nYour roles will then be automatically applied.',
        inline=False)
    embed_step3.set_image(url='https://media.discordapp.net/attachments/709907130102317093/904744444539076618/unknown.png')

    try:
        await member.send(embed=embed_step1)
        await member.send(embed=embed_step2)
        await member.send(embed=embed_step3)
    except Forbidden:
        await reply(ctx, 'Whoops! I cannot DM you after all due to your privacy settings. Please allow DMs from other server members and try again.', send_followup=False)
    except HTTPException:
        await reply(ctx, 'An unexpected error happened (HTTP 400, bad request). Please contact an Administrator.', send_followup=False)
        return


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
