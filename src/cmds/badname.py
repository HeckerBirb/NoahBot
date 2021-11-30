from discord.ext import commands
from discord.commands.context import ApplicationContext
from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID
from src.cmds.proxy_helpers import Reply


def name():
    return 'badname'


def description():
    return 'Changes the nickname of a user to ChangeMe.'


async def perform_action(ctx: ApplicationContext, reply):
    await reply(ctx, 'Not implemented yet...')


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)

#    async def badname(
#            self,
#            ctx,
#            member: Option(discord.Member, "The member to badname", required=True),
#    ):
#        """Remove a users bad discord name!"""
#        moderator = ctx.author
#        try:  # Check if the user exists
#            oldname = member.display_name
#            await member.edit(nick=f"ChangeMe")
#            await ctx.channel.send(f"{member.name}'s name has been updated to ChangeMe")
#            try:
#                await member.send("Hello! It has been determined by a member of the staff team that your nickname "
#                                  "was breaking the rules. It has been automagically updated to 'ChangeMe'. "
#                                  "Please refer to #rules when creating a name.")
#            except:
#                await ctx.send("User has DMs disabled; DM not sent.")
#            await InfractionRecord.insertInfraction(member,
#                                                    moderator,
#                                                    0,
#                                                    f"User had a bad name of {oldname}",
#                                                    ctx.guild.id)
#        except Exception as e:
#            # The user is invalid
#
#            await ctx.channel.send(f" {moderator.mention} Please specify a valid user.")
#            raise e
#
#
#
#