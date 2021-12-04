from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply

"""
CREATE TABLE `htb_discord_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_identifier` varchar(255) NOT NULL,
  `discord_user_id` varchar(42) NOT NULL,
  `htb_user_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `htb_discord_link`
SELECT
    id, token, user, htbuser
FROM token;
"""


def name():
    return 'verify'


def description():
    return 'Receive instructions in a DM on how to identify yourself with your HTB account.'


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
