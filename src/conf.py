import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands

from src.log4noah import STDOUT_LOG


def _get_int_env(env_var: str, default: str = None) -> int:
    try:
        STDOUT_LOG.debug(f'Loading {env_var} (default={default}).')
        return int(os.getenv(env_var, default))
    except KeyError:
        STDOUT_LOG.critical(f'Environment variable {env_var} cannot be parsed as an int!')
        exit(1)


ROOT_DIR = Path(dirname(dirname(abspath(__file__))))

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = _get_int_env('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'noahbot')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASSWORD', None)
if MYSQL_PASS is None:
    MYSQL_PASS = os.getenv('MYSQL_ROOT_PASSWORD', 'noah')

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
    COMMUNITY_MANAGER = _get_int_env('COMMUNITY_MANAGER_ROLE')
    ADMINISTRATOR = _get_int_env('ADMINISTRATOR_ROLE')
    SR_MODERATOR = _get_int_env('SR_MODERATOR_ROLE')
    MODERATOR = _get_int_env('MODERATOR_ROLE')
    MUTED = _get_int_env('MUTED_ROLE')

    # Ranks
    OMNISCIENT = _get_int_env('OMNISCIENT_ROLE')
    GURU = _get_int_env('GURU_ROLE')
    ELITE_HACKER = _get_int_env('ELITE_HACKER_ROLE')
    PRO_HACKER = _get_int_env('PRO_HACKER_ROLE')
    HACKER = _get_int_env('HACKER_ROLE')
    SCRIPT_KIDDIE = _get_int_env('SCRIPT_KIDDIE_ROLE')
    NOOB = _get_int_env('NOOB_ROLE')
    VIP = _get_int_env('VIP_ROLE')
    VIP_PLUS = _get_int_env('VIP_PLUS_ROLE')

    # Content Creation
    CHALLENGE_CREATOR = _get_int_env('CHALLENGE_CREATOR_ROLE')
    BOX_CREATOR = _get_int_env('BOX_CREATOR_ROLE')

    # Positions
    RANK_ONE = _get_int_env('RANK_ONE_ROLE')
    RANK_FIVE = _get_int_env('RANK_FIVE_ROLE')
    RANK_TEN = _get_int_env('RANK_TEN_ROLE')
    RANK_TWENTY_FIVE = _get_int_env('RANK_TWENTY_FIVE_ROLE')
    RANK_FIFTY = _get_int_env('RANK_FIFTY_ROLE')
    RANK_HUNDRED = _get_int_env('RANK_HUNDRED_ROLE')

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
