import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands

# TODO: Update this page before go-live

GUILD_ID = 368879044999118848

ROOT_DIR = Path(dirname(dirname(abspath(__file__))))

MYSQL_URI = os.getenv('MYSQL_URI', 'localhost')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'noahbot')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASS', 'noah')

HTB_URL = 'https://www.hackthebox.com'
API_URL = f'{HTB_URL}/api'
API_V4_URL = f'{API_URL}/v4'
IDENTIFY_BASE_URL = f'{API_URL}/users/identifier'
# PROFILE_BASE_URL = f'{HTB_URL}/home/users/profile'
# TOURNAMENT_WINS_BASE_URL = f'{API_V4_URL}/bg/tournament/winners'

JOINABLE_ROLES = {
    'Noah Gang': 915400469164220417,
    'Buddy Gang': 915400523035852800,
    'Red Team': 915400555009028128,
    'Blue Team': 915402415971389451
}


class ChannelIDs:
    SR_MODERATOR = 407195797269118977


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    COMMUNITY_MANAGER = 707322172267560991
    ADMINISTRATOR = 506943166365302789
    SR_MODERATOR = 708371481448546354
    MODERATOR = 486603600085123073

    MUTED = 411882315141087232

    # TODO: Remove these two
    POLLOS_HERMANOS = 407196347486306314
    SEMI_POWERS = 411892864537329685

    ALL_ADMINS = [ADMINISTRATOR, COMMUNITY_MANAGER, POLLOS_HERMANOS]
    ALL_SR_MODERATOR = []
    ALL_MODS = [MODERATOR, SEMI_POWERS]


class SlashPerms:
    """ IDs for the specific roles. Note that due to the way slash commands handle permissions, these are SINGULAR. """
    ADMIN = _allow(RoleIDs.POLLOS_HERMANOS)
    SR_MODERATOR = _allow(RoleIDs.SR_MODERATOR)
    MODERATOR = _allow(RoleIDs.SEMI_POWERS)


class PrefixPerms:
    """ IDs for the specific roles. Note that due to the way prefix commands handle permissions, these are PLURAL. """
    ALL_ADMINS = RoleIDs.ALL_ADMINS
    ALL_SR_MODERATORS = RoleIDs.ALL_SR_MODERATOR
    ALL_MODS = RoleIDs.ALL_MODS
