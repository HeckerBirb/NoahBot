from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument, MissingPermissions, UserInputError, CommandNotFound, NoPrivateMessage


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
        elif isinstance(error, UserInputError):
            message = 'Something about your input was wrong, please check your input and try again.'
        elif isinstance(error, NoPrivateMessage):
            message = 'This command cannot be run in a DM.'

        if message is None:
            raise error
        else:
            await ctx.send(message, delete_after=15)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
