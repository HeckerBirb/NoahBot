import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands

GUILD_ID = os.getenv('GUILD_ID', None)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ROOT_DIR = Path(dirname(dirname(abspath(__file__))))

MYSQL_URI = os.getenv('MYSQL_URI', 'localhost')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'noahbot')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASS', 'noah')

HTB_API_SECRET = os.getenv('HTB_API_SECRET', None)
HTB_URL = 'https://www.hackthebox.com'
API_URL = f'{HTB_URL}/api'
API_V4_URL = f'{API_URL}/v4'

JOINABLE_ROLES = {
    'Noah Gang': 754405726432133261,
    'Buddy Gang': 856506360999837737,
    'Red Team': 703614597009113118,
    'Blue Team': 703614467971350578
}


class ChannelIDs:
    SR_MODERATOR = 732712216641667082
    BOT_LOGS = 756974286081622136


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    # Moderation
    COMMUNITY_MANAGER = 707322172267560991
    ADMINISTRATOR = 506943166365302789
    SR_MODERATOR = 708371481448546354
    MODERATOR = 486603600085123073
    MUTED = 411882315141087232

    # Ranks
    OMNISCIENT = 586528519459438592
    GURU = 586528488346091520
    ELITE_HACKER = 586528352655900673
    PRO_HACKER = 586528166739443712
    HACKER = 586528079363702801
    SCRIPT_KIDDIE = 586529669491326976
    NOOB = 586527620737269765
    VIP = 586528637658988550
    VIP_PLUS = 833723601336664085

    # Content Creation
    CHALLENGE_CREATOR = 548239933454680096
    BOX_CREATOR = 531205748592607232

    # Positions
    ONE = 586529401156665364
    FIVE = 586529381099372554
    TEN = 586529358735474688
    TWENTY_FIVE = 586529313579597844
    FIFTY = 586529293207601162
    HUNDRED = 586529258038493197

    @staticmethod
    def get_post_or_rank(what: int) -> int:
        return {
            1: RoleIDs.ONE,
            5: RoleIDs.FIVE,
            10: RoleIDs.TEN,
            25: RoleIDs.TWENTY_FIVE,
            50: RoleIDs.FIFTY,
            100: RoleIDs.HUNDRED,
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
    ALL_POSITIONS = [ONE, FIVE, TEN, TWENTY_FIVE, FIFTY, HUNDRED]


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
