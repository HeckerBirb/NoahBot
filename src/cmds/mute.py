from src.noahbot import bot

# Should contain all moderation commands, such as /warn /strike /ban /whois /badname etc.import typing
#
# # Import Discord Objects
# import discord
# from discord import HTTPException
# from discord.ext import tasks
# from discord.commands import slash_command, Option, commands
#
# # Import Database Utils
# from util.database.IgnoredOperations import IgnoredRecord
# from util.database.InfractionTransactions import InfractionRecord
# from util.database.MutedMemberTransactions import MuteRecord
# from util.database.BanRecordOperations import BanRecord
# from util.checkModerationStatus import checkMod, checkAdmin, checkOwner, cmm
# from util.database.MiscOperations import MiscOperations
#
#
# import calendar
# import datetime
# import time
#
# # Import Logging
# from botlogger import BOT_LOG
#
# from configuration import GroupAdministrator, GroupModerator, slash_guild, htb_guild, Muted, not_allowed_to_mention, ApprovalChannel, BASE_URL, MessageLogChannel, GroupSrMod
#
#
#
# class Moderation(discord.ext.commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         # self.check_muted.start()
#         # self.check_banned.start()
#
#     def cog_unload(self):
#         """
#         This function is the standard handler called upon module reload
#         Adds before, after, author, and channel to database. Logs message to logging channel containing the changes.
#         """
#         # self.check_muted.cancel()
#         # self.check_banned.cancel()
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=False,
#         permissions = [
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def mute(
#         self,
#         ctx,
#         member: Option(discord.Member, "Pick a member to mute", required=True),
#         length: Option(str, "How long to mute the member for", required=True),
#         message: Option(str, "What message to send to the muted member", required=True),
#     ):
#         """Mutes a member for the given time"""
#
#         dur = await MiscOperations.parse_duration_str(length)
#         if not dur:
#             return await ctx.send("Invalid time option entered!")
#         epoch_time = calendar.timegm(time.gmtime())
#         if dur - epoch_time <= 0:
#             return await ctx.send("Ban length must be greater then 0.")
#         await MuteRecord.muteMember(dur, message, ctx.author, member, ctx.guild.id)
#         role = self.bot.get_guild(htb_guild).get_role(Muted)
#         await member.add_roles(role)
#         await ctx.respond(f"User {member.mention} has been muted for {length}")
#         try:
#             await member.send(f"Hello, you have been muted for {length} due to {' '.join(message)}", allowed_mentions=not_allowed_to_mention)
#         except Exception as e:
#             await ctx.respond(f"Member {member.mention} has DM's disabled, unable to DM.")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def unmute(
#             self,
#             ctx,
#             member: Option(discord.Member, "Pick a member to unmute", required=True),
#         ):
#         """Unmutes a member!"""
#         role = self.bot.get_guild(htb_guild).get_role(Muted)
#         await MuteRecord.unmuteMember(member)
#         await member.remove_roles(role)
#         await ctx.respond(f"{member.mention} has been unmuted")
#         try:
#             await member.send(f"Hello {member.mention}, your muted has been manually removed by a staff member.")
#         except Exception as e:
#             await ctx.respond(f"Member {member.mention} has disabled their DM's")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def setstatus(
#         self,
#         ctx,
#         status: Option(str, "What status to set the bot to", required=True),
#     ):
#         """Sets the bots status"""
#         await self.bot.change_presence(activity=discord.Game(name=f'{status}'))
#         await ctx.respond(f"Status set to {status}")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def slowmode(
#             self,
#             ctx,
#             seconds: Option(int, "How long to slowmode for", required=True, default=5),
#             channel: Option(discord.TextChannel, "What channel to slowmode, If blank current one is used", required=False),
#         ):
#         """Sets a slowmode on a channel"""
#         if channel is None:
#             channel = ctx.channel
#         if seconds <= 0:
#             seconds = 0
#         if seconds >= 21599:
#             seconds = 21599
#         await channel.edit(slowmode_delay=seconds)
#         await ctx.respond(
#                 f"Set the slowmode delay in this {channel.name} to {seconds} seconds!",
#                 ephemeral=True
#             )
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def cleanup(
#             self,
#             ctx,
#             count: Option(int, "How many messages to delete", required=True, default=5),
#         ):
#         """Removes the past X messages"""
#         await ctx.channel.purge(limit=count + 1, bulk=True, check=lambda m: m != ctx.message)
#         # Don't delete the command that triggered this deletion
#         await ctx.respond(
#             f"Deleted {count} messages.",
#             ephemeral=True
#         )
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupModerator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def ban(
#             self,
#             ctx,
#             member: Option(discord.Member, "Pick a member to ban", required=True),
#             length: Option(str, "How long to ban the member for", required=True),
#             message: Option(str, "What message to send to the banned member", required=True),
#         ):
#         """Bans a user temporaily"""
#         perma_ban = False
#         reason = message
#         dur = await MiscOperations.parse_duration_str(length)
#         if not dur:
#             return await ctx.send("Invalid time option entered!")
#         epoch_time = calendar.timegm(time.gmtime())
#         needs_approval = 0
#
#         if cmm(member):
#             return await ctx.send("You cannot ban another staff member.")
#
#         if dur - epoch_time <= 0:
#             return await ctx.send("Ban length must be greater then 0.")
#         elif dur - epoch_time >= 31536000:  # Over One Year
#             perma_ban = True
#
#         if perma_ban:
#             BOT_LOG.debug("Ban is over 1y, requesting permaban")
#             ban_details = await BanRecord.banMember(dur, reason, ctx.author, member, ctx.guild.id, perma=True)
#         if not perma_ban:
#             ban_details = await BanRecord.banMember(dur, reason, ctx.author, member, ctx.guild.id)
#             try:
#                 await member.send(
#                     f"You have been banned from {ctx.guild.name} for '{reason}'. "
#                     f"You may rejoin after {length} with invite code discord.gg/hackthebox")
#                 await ctx.guild.ban(member, reason=reason)
#             except Exception as E:
#                 await ctx.respond("The Bot Failed to DM", ephemeral=True)
#                 await ctx.guild.ban(member, reason=reason)
#         await InfractionRecord.insertInfraction(member, ctx.author, 0,
#                                                 f"{member.display_name} has been banned for a duration of "
#                                                 f"{length} for \"{reason}\"",
#                                                 ctx.guild.id)
#
#         if needs_approval:
#             if not perma_ban:
#                 embed = discord.Embed(title=f"Ban {ban_details[0][0]} Length Request",
#                                       description=f"{ctx.author.name} would like to ban {member.name} for "
#                                                   f"{length} for \"{reason}\"")
#             else:
#                 embed = discord.Embed(title=f"Permaban Request",
#                                       description=f"{ctx.author.name} would like to ban {member.name}"
#                                                   f" permanently for \"{reason}\"")
#             embed.set_thumbnail(url=f"{BASE_URL}/images/logo600.png")
#             embed.add_field(name="To Approve",
#                             value=f"++approve {ban_details[0][0]}", inline=True)
#             embed.add_field(name="To Change",
#                             value=f"++dispute {ban_details[0][0]} (time, Note: Time is from now, not original ban.)",
#                             inline=True)
#             embed.add_field(
#                 name="To Deny", value=f"++deny {ban_details[0][0]}", inline=True)
#             await self.bot.get_guild(htb_guild).get_channel(ApprovalChannel).send(embed=embed)
#         if not perma_ban:
#             await ctx.respond(
#                 f"{member.display_name} has been banned for a duration of {length} for \"{reason}\"",
#                 allowed_mentions=not_allowed_to_mention)
#         else:
#             await ctx.respond(f"{member.mention} was requested to be banned forever.")
#
#     # TODO: https://gist.github.com/MhmCats/500eafdad0aaf278b94c612764688976 / Implement Buttons
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupSrMod,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def approve(
#             self,
#             ctx,
#             banid: Option(int, "The ID of the ban to approve", required=True),
#         ):
#         """Approves a ban request!"""
#         discord_id = banid
#         stuff = await BanRecord.checkApproval(discord_id)
#         if stuff[0][4] == 1921424673:
#             BOT_LOG.debug(f'Processing ban record: {discord_id}')
#             guild = self.bot.get_guild(int(htb_guild))
#             try:
#                 member = await guild.fetch_member(int(stuff[0][1]))
#                 await member.send(f"You have been banned from {ctx.guild.name} for '{stuff[0][2]}'")
#                 await guild.ban(member, reason=stuff[0][2], delete_message_days=0)
#             except HTTPException as ex:
#                 BOT_LOG.debug(
#                     f'Failed to GET the user ID #{discord_id} from Discord.', ex)
#                 await ctx.respond(f"User with ID #{discord_id} not found.")
#
#         if stuff[0][6] == 1:
#             return await ctx.send("This ban has already been approved.")
#         await BanRecord.changeBanStatus(discord_id, "approve")
#         await ctx.respond("Ban Approved.")
#
#         banning_mod = await self.bot.fetch_user(stuff[0][3])
#         await banning_mod.send(f"Your Ban Request on {stuff[0][1]} for {stuff[0][2]} has been approved!")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupSrMod,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def dispute(
#             self,
#             ctx,
#             banid: Option(int, "The ID of the ban to dispute", required=True),
#             length: Option(int, "The length of the new ban", required=True),
#         ):
#         """Change a pending ban's length!"""
#         _id = banid
#         status_of_ban = await BanRecord.checkApproval(_id)
#         status_of_first_ban = status_of_ban[
#             0]
#         # Since this is a database call, the data we need is in an array.
#         # However, since the ID field is unique only one ID will ever return,
#         # and it will be the first object in the array
#         if status_of_first_ban[6] == 1:
#             return await ctx.send("This ban has already been approved.")
#         dur = await MiscOperations.parse_duration_str(length[0])
#         if not dur:
#             return await ctx.send("Invalid time option entered!")
#         await BanRecord.changeBanStatus(_id, "change", dur)
#         await ctx.respond("Ban updated.")
#         banning_mod = await self.bot.fetch_user(status_of_first_ban[3])
#         await banning_mod.send(
#             f"Your Ban Request on {status_of_first_ban[1]} for "
#             f"{status_of_first_ban[2]} has been changed to {length[0]}!")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             ),
#             commands.Permission(
#                 id=GroupSrMod,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def deny(
#             self,
#             ctx,
#             banid: Option(int, "The ID of the ban to deny", required=True),
#         ):
#         """Deny a pending ban"""
#         ban_id = banid
#         dur = 1
#         status_of_ban = await BanRecord.checkApproval(ban_id)
#         await BanRecord.changeBanStatus(ban_id, "change", dur)
#         await ctx.respond("Member has been unbanned!")
#         banning_mod = await self.bot.fetch_user(status_of_ban[0][3])
#         await banning_mod.send(f"Your Ban Request on {status_of_ban[0][1]} for {status_of_ban[0][2]} has been denied!")
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def unban(
#         self,
#         ctx,
#         user_id: Option(int, "The ID of the user to unban", required=True),
#     ):
#         """Unban a user"""
#         try:
#             member = await self.bot.fetch_user(user_id)
#             await BanRecord.unbanMember(member.id, ctx.guild.id)
#             await self.bot.get_channel(MessageLogChannel).send(
#                 f"Unbanned {member.name} due to {ctx.author.display_name}")
#             await ctx.guild.unban(member)
#             await ctx.respond(f"Member {member.name} unbanned")
#         except:
#             await ctx.respond("Member with ID Doesnt exist, or is not banned", ephemeral=True)
#
#     @slash_command(
#         guild_ids=slash_guild,
#         default_permission=True,
#         permissions=[
#             commands.Permission(
#                 id=GroupAdministrator,
#                 type=1,
#                 permission=True
#             )
#         ]
#     )
#     async def blacklistlogs(
#             self,
#             ctx,
#             channel: Option(discord.TextChannel, "The channel to blacklist", required=True),
#         ):
#         """Blacklists a channel from being seen in logs!"""
#         await MiscOperations.blacklistChannel(channel.name, ctx.guild.id)
#         await ctx.respond(f"{channel} has been added to the log blacklist")
#
#     # This function is used for check for muted members. Runs every 30 seconds.
#     # Returns logging message indicating member that was unmuted.
#     # Logs error if unable to retrieve records.
#     @tasks.loop(seconds=29)
#     async def check_muted(self):
#         BOT_LOG.info("Checking if anyone needs to be unmuted...")
#         res = await MuteRecord.getExpiredMutes()
#         try:
#             BOT_LOG.debug(
#                 f"Got list of recorded mutes. List is {len(res)} accounts long.")
#             for i in res:
#                 BOT_LOG.debug(f'Processing mute record: {i}')
#                 guild = self.bot.get_guild(int(i.guildID))
#                 if guild is None:
#                     BOT_LOG.info(
#                         f"Guild cannot be found! Guild is {guild}. Continuing...")
#                     continue
#                 BOT_LOG.debug(f"Guild ID for unmuting members: {guild}")
#                 try:
#                     member = await guild.fetch_member(int(i.member))
#                 except Exception as e:
#                     BOT_LOG.info(
#                         "Muted user seems to have left the server. Removing Instance from database.")
#                     BOT_LOG.debug(f'Error message: "{e}".')
#                     left_user = await self.bot.fetch_user(int(i.member))
#                     await MuteRecord.unmuteMember(left_user)
#                     BOT_LOG.debug(
#                         f'Removed user "{left_user}" from the database.')
#                     return
#
#                 if member is None:
#                     BOT_LOG.debug(
#                         'Was not able to fetch the member ID even though it should,'
#                         'as the member has not left the server.')
#                     BOT_LOG.debug(f'Row from database: {i}')
#                     BOT_LOG.debug('Continuing...')
#                     continue
#
#                 name_to_use = member.name
#                 name_to_use = name_to_use.replace("@", "")
#                 BOT_LOG.debug(f"UnMuted {name_to_use}")
#                 await self.bot.get_channel(BotSystemLogsChannel).send(f'Unmuted "{name_to_use}".')
#                 muted_role = guild.get_role(Muted)
#                 await member.remove_roles(muted_role)
#                 try:
#                     await member.send(f"Hello {member.mention}, your mute has automatically expired.")
#                 except Exception as e:
#                     BOT_LOG.debug(f"Unable to inform {member.id} of unmute")
#             BOT_LOG.debug("Dropping unmuted people from DB")
#             await MuteRecord.dropExpiredMutes()
#
#             BOT_LOG.info("Mutes processed.")
#         except Exception as e:
#             BOT_LOG.error(exception=e)
#
#     # This function is used for check for banned members. Runs every 30 seconds.
#     # Retrieves ban records with a timestamp in the past from db.
#     # Returns logging message indicating member that was unbanned.
#     # Logs error if unable to retrieve records.
#     @tasks.loop(seconds=47)
#     async def check_banned(self):
#         BOT_LOG.info("Checking bans...")
#         res = await BanRecord.getExpiredBans()
#         BOT_LOG.debug(
#             f"Got list of recorded bans. List is {len(res)} accounts long.")
#         try:
#             for i in res:
#                 guild = self.bot.get_guild(int(i.guildID))
#                 member = await self.bot.fetch_user(int(i.member))
#                 BOT_LOG.debug(f'Attempting to unban "{member.name}"...')
#                 try:
#                     await guild.unban(member)
#                 except Exception as e:
#                     BOT_LOG.error(
#                         log_message=f"Issue unbanning member {member.display_name}", error=e)
#                 await BanRecord.dropExpiredBans(i.guildID)
#                 await self.bot.get_channel(BotSystemLogsChannel).send(f'Unbanned "{member.name}".')
#             BOT_LOG.info("Bans Processed")
#         except Exception as e:
#             BOT_LOG.error(f"{e}")
#
#
#
# def setup(bot):
#     bot.add_cog(Moderation(bot))


def setup(le_bot):
    # le_bot.add_command(some_func)
    pass
