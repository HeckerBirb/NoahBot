class Reply:
    """ Proxy for ctx.send and ctx.respond. """
    @staticmethod
    async def slash(ctx, msg):
        await ctx.respond(msg)

    @staticmethod
    async def prefix(ctx, msg):
        await ctx.send(msg)
