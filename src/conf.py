import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands


ROOT_DIR = Path(dirname(dirname(abspath(__file__))))
MYSQL_URI = os.getenv('MYSQL_URI', 'localhost')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'noahbot')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASS', 'noah')

GUILD_ID = 368879044999118848


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    POLLOS_HERMANOS = 407196347486306314
    SEMI_POWERS = 411892864537329685


class SlashPerms:
    """ IDs for the specific roles. Note that due to the way slash commands handle permissions, these are SINGULAR. """
    ADMIN = _allow(RoleIDs.POLLOS_HERMANOS)
    MODERATOR = _allow(RoleIDs.SEMI_POWERS)


class PrefixPerms:
    """ IDs for the specific roles. Note that due to the way prefix commands handle permissions, these are PLURAL. """
    ALL_ADMINS = ['Administrator', RoleIDs.POLLOS_HERMANOS]
    ALL_MODS = ['Moderator', RoleIDs.SEMI_POWERS]
