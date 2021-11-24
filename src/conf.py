from discord.commands import commands


GUILD_ID = 368879044999118848


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    POLLOS_HERMANOS = 407196347486306314
    SEMI_POWERS = 411892864537329685


class SlashPerms:
    class RoleID:
        ADMINISTRATORS = RoleIDs.POLLOS_HERMANOS
        MODERATORS = RoleIDs.SEMI_POWERS

    ADMINISTRATORS = _allow(RoleID.ADMINISTRATORS)
    MODERATORS = _allow(RoleID.MODERATORS)


class PrefixPerms:
    ADMINISTRATORS = ['Administrator', RoleIDs.POLLOS_HERMANOS]
    MODERATORS = ['Moderator', RoleIDs.SEMI_POWERS]
