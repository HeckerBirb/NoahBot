from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply, perform_temp_ban

"""
CREATE TABLE IF NOT EXISTS `ban_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(42) NOT NULL,
  `reason` text NOT NULL,
  `moderator` varchar(42) NOT NULL,
  `unban_time` int(42) NOT NULL,
  `approved` boolean NOT NULL,
  `unbanned` boolean NOT NULL DEFAULT 0,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE `ban_record`;

INSERT INTO `ban_record`
SELECT
    id, member, reason, moderator, unbanTime, CASE WHEN approved = 1 THEN 1 ELSE 0 END as approved, 0, CURRENT_TIMESTAMP
FROM hotbot.BanRecords;
"""


def name():
    return 'tempban'


def description():
    return 'Ban a user from the server temporarily.'


# TODO: should have an auto-unban functionality
async def perform_action(ctx, reply, user_id, duration, reason, needs_approval=True, banned_by_bot=False):
    await perform_temp_ban(bot, ctx, reply, user_id, duration, reason, needs_approval=True, banned_by_bot=False)


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        duration: Option(str, 'Duration of the ban in human-friendly notation, e.g. 2mo for two months or 3w for three weeks.'),
        reason: Option(str, 'Ban reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, duration, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, duration: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, duration, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
