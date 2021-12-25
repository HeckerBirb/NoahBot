import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands

GUILD_ID = os.getenv('GUILD_ID', None)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ROOT_DIR = Path(dirname(dirname(abspath(__file__))))

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', 'localhost')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'noahbot')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASS', 'noah')

HTB_API_SECRET = os.getenv('HTB_API_SECRET', None)
HTB_URL = 'https://www.hackthebox.com'
API_URL = f'{HTB_URL}/api'
API_V4_URL = f'{API_URL}/v4'

JOINABLE_ROLES = {
    'Noah Gang': os.getenv('NOAH_GANG_ROLE'),
    'Buddy Gang': os.getenv('BUDDY_GANG_ROLE'),
    'Red Team': os.getenv('RED_TEAM_ROLE'),
    'Blue Team': os.getenv('BLUE_TEAM_ROLE')
}


class ChannelIDs:
    SR_MODERATOR = os.getenv('SR_MOD_CHAN')
    BOT_LOGS = os.getenv('BOT_LOGS_CHAN')


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    # Moderation
    COMMUNITY_MANAGER = os.getenv('COMMUNITY_MANAGER_ROLE')
    ADMINISTRATOR = os.getenv('ADMINISTRATOR_ROLE')
    SR_MODERATOR = os.getenv('SR_MODERATOR_ROLE')
    MODERATOR = os.getenv('MODERATOR_ROLE')
    MUTED = os.getenv('MUTED_ROLE')

    # Ranks
    OMNISCIENT = os.getenv('OMNISCIENT_ROLE')
    GURU = os.getenv('GURU_ROLE')
    ELITE_HACKER = os.getenv('ELITE_HACKER_ROLE')
    PRO_HACKER = os.getenv('PRO_HACKER_ROLE')
    HACKER = os.getenv('HACKER_ROLE')
    SCRIPT_KIDDIE = os.getenv('SCRIPT_KIDDIE_ROLE')
    NOOB = os.getenv('NOOB_ROLE')
    VIP = os.getenv('VIP_ROLE')
    VIP_PLUS = os.getenv('VIP_PLUS_ROLE')

    # Content Creation
    CHALLENGE_CREATOR = os.getenv('CHALLENGE_CREATOR_ROLE')
    BOX_CREATOR = os.getenv('BOX_CREATOR_ROLE')

    # Positions
    RANK_ONE = os.getenv('RANK_ONE_ROLE')
    RANK_FIVE = os.getenv('RANK_FIVE_ROLE')
    RANK_TEN = os.getenv('RANK_TEN_ROLE')
    RANK_TWENTY_FIVE = os.getenv('RANK_TWENTY_FIVE_ROLE')
    RANK_FIFTY = os.getenv('RANK_FIFTY_ROLE')
    RANK_HUNDRED = os.getenv('RANK_HUNDRED_ROLE')

    @staticmethod
    def get_post_or_rank(what: int) -> int:
        return {
            1: RoleIDs.RANK_ONE,
            5: RoleIDs.RANK_FIVE,
            10: RoleIDs.RANK_TEN,
            25: RoleIDs.RANK_TWENTY_FIVE,
            50: RoleIDs.RANK_FIFTY,
            100: RoleIDs.RANK_HUNDRED,
            'Omniscient': RoleIDs.OMNISCIENT,
            'Guru': RoleIDs.GURU,
            'Elite Hacker': RoleIDs.ELITE_HACKER,
            'Pro Hacker': RoleIDs.PRO_HACKER,
            'Hacker': RoleIDs.HACKER,
            'Script Kiddie': RoleIDs.SCRIPT_KIDDIE,
            'Noob': RoleIDs.NOOB,
            'vip': RoleIDs.VIP,
            'dedivip': RoleIDs.VIP_PLUS,
            'Challenge Creator': RoleIDs.CHALLENGE_CREATOR,
            'Box Creator': RoleIDs.BOX_CREATOR
        }.get(what)

    # Role collections
    ALL_ADMINS = [ADMINISTRATOR, COMMUNITY_MANAGER]
    ALL_SR_MODERATOR = [SR_MODERATOR]
    ALL_MODS = [SR_MODERATOR, MODERATOR]
    ALL_RANKS = [OMNISCIENT, GURU, ELITE_HACKER, PRO_HACKER, HACKER, SCRIPT_KIDDIE, NOOB, VIP, VIP_PLUS]
    ALL_CREATORS = [BOX_CREATOR, CHALLENGE_CREATOR]
    ALL_POSITIONS = [RANK_ONE, RANK_FIVE, RANK_TEN, RANK_TWENTY_FIVE, RANK_FIFTY, RANK_HUNDRED]


class SlashPerms:
    """ IDs for the specific roles. Note that due to the way slash commands handle permissions, these are SINGULAR. """
    COMMUNITY_MANAGER = _allow(RoleIDs.COMMUNITY_MANAGER)
    ADMIN = _allow(RoleIDs.ADMINISTRATOR)
    SR_MODERATOR = _allow(RoleIDs.SR_MODERATOR)
    MODERATOR = _allow(RoleIDs.MODERATOR)


class PrefixPerms:
    """ IDs for the specific roles. Note that due to the way prefix commands handle permissions, these are PLURAL. """
    ALL_ADMINS = RoleIDs.ALL_ADMINS
    ALL_SR_MODERATORS = RoleIDs.ALL_SR_MODERATOR
    ALL_MODS = RoleIDs.ALL_MODS
