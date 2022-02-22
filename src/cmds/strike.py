from discord.commands import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands

from src.cmds._proxy_helpers import Reply, perform_infraction_record
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.noahbot import bot

"""
CREATE TABLE IF NOT EXISTS `infraction_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` mediumtext NOT NULL,
  `weight` int(11) NOT NULL,
  `moderator` varchar(18) NOT NULL,
  `date` DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE `infraction_record`;

INSERT INTO infraction_record
SELECT
    id, member, reason, strikes, moderator, date
FROM hotbot.Strikes;
"""


def name():
    return 'strike'


def description():
    return 'Strike the user with the selected weight. DMs the user about the strike and the reason why.'


async def perform_action(ctx: ApplicationContext, reply, user_id, weight, reason):
    await perform_infraction_record(ctx, reply, bot.guilds[0], user_id, weight, reason)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        reason: Option(str, 'Strike reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, '1', reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, '1', ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
