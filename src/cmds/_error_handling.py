from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """A global error handler cog."""

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, MissingRequiredArgument):
            message = f'Parameter "{error.param.name}" is required, but missing. Type `{ctx.clean_prefix}help {ctx.invoked_with}` for help.'
        elif isinstance(error, commands.MissingPermissions):
            message = 'You are missing the required permissions to run this command.'
        elif isinstance(error, commands.UserInputError):
            message = 'Something about your input was wrong, please check your input and try again.'
        else:
            message = 'Oh no! Something went wrong while running the command...'
        await ctx.send(message, delete_after=5)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
