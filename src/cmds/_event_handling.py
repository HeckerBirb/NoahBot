from discord import Member
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument, MissingPermissions, UserInputError, CommandNotFound, \
    NoPrivateMessage, MissingAnyRole

from src.automation.auto_verify import process_reverify
from src.log4noah import STDOUT_LOG


class interruptable:
    """ Allow the ability to "break out of" a with-statement, just like how `break` will break out of a loop. """
    class Interrupt(Exception):
        """ Exception to raise when wanting to break out of the with-statement. """

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, error_type, value, traceback):
        error = self.value.__exit__(error_type, value, traceback)
        if error_type == self.Interrupt:
            return True
        return error


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """A global error handler cog."""

        message = None
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingRequiredArgument):
            message = f'Parameter "{error.param.name}" is required, but missing. Type `{ctx.clean_prefix}help {ctx.invoked_with}` for help.'
        elif isinstance(error, MissingPermissions):
            message = 'You are missing the required permissions to run this command.'
        elif isinstance(error, MissingAnyRole):
            message = 'You are not authorized to use that command.'
        elif isinstance(error, UserInputError):
            message = 'Something about your input was wrong, please check your input and try again.'
        elif isinstance(error, NoPrivateMessage):
            message = 'This command cannot be run in a DM.'

        if message is None:
            raise error
        else:
            STDOUT_LOG.debug(f'A user caused and error which was handled. Message: "{message}".')
            await ctx.send(message, delete_after=15)


class MessageHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx: commands.Context):
        await process_reverify(ctx.author)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        await process_reverify(member)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(MessageHandler(bot))
