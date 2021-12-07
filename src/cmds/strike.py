from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply

"""
CREATE TABLE `infraction_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` mediumtext NOT NULL,
  `weight` int(11) NOT NULL,
  `moderator` varchar(18) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO infraction_record
SELECT
    id, member, reason, strikes, moderator, date
FROM Strikes;
"""


def name():
    return 'strike'


def description():
    return 'Strike the user with the selected weight. DMs the user about the strike and the reason why.'


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)  # TODO: ' '.join(reason)


def setup(le_bot):
    le_bot.add_command(action_prefix)
