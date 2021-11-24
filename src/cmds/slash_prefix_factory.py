# Generic slash commands functionality goes here. Should support most cases so that new commands are trivial.
# Should include an optional "persistence plugin" which will dictate where the output of the cmd is persisted and how.

class Reply:
    """ Proxy for ctx.send and ctx.respond. """
    @staticmethod
    async def _slash(ctx, msg):
        await ctx.respond(msg)

    @staticmethod
    async def _prefix(ctx, msg):
        await ctx.send(msg)

    SLASH = _slash
    PREFIX = _prefix

