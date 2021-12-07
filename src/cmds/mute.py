from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds._proxy_helpers import Reply


def name():
    return 'mute'


def description():
    return 'Mute a person (adds the Muted role to person).'


# TODO: should have an auto-unmute functionality
async def perform_action(ctx: ApplicationContext, reply, user_id, duration, reason):
    #dur = await MiscOperations.parse_duration_str(length)
    #if not dur:
    #    return await ctx.send("Invalid time option entered!")
    #epoch_time = calendar.timegm(time.gmtime())
    #if dur - epoch_time <= 0:
    #    return await ctx.send("Ban length must be greater then 0.")
    #await MuteRecord.muteMember(dur, message, ctx.author, member, ctx.guild.id)
    #role = self.bot.get_guild(htb_guild).get_role(Muted)
    #await member.add_roles(role)
    #await ctx.respond(f"User {member.mention} has been muted for {length}")
    #try:
    #    await member.send(f"Hello, you have been muted for {length} due to {message}",
    #                      allowed_mentions=not_allowed_to_mention)
    #except Exception as e:
    #    await ctx.respond(f"Member {member.mention} has DM's disabled, unable to DM.")
#

    if len(reason) == 0:
        reason = 'Time to shush, innit?'

    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(
        ctx: ApplicationContext,
        user_id: Option(str, 'User ID or @mention name.'),
        duration: Option(str, 'Duration of the mute in human-friendly notation, e.g. 10m for ten minutes or 1d for one day.'),
        reason: Option(str, 'Mute reason. Will be sent to the user in a DM as well.')
):
    await perform_action(ctx, Reply.slash, user_id, duration, reason)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id: str, duration: str, *reason: str):
    await perform_action(ctx, Reply.prefix, user_id, duration, ' '.join(reason))


def setup(le_bot):
    le_bot.add_command(action_prefix)
