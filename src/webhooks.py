from aiohttp import web
import asyncio
import discord
from discord import  Role, Guild
from discord.ext import commands
from os import environ
from src.conf import RoleIDs

from typing import Optional, List
from enum import Enum

class WebhookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_academy_role(self, guild: Guild, cert: str) -> Optional[Role]:
        roles = {"HTB Certified Bug Bounty Hunter": "CBBH_ROLE"}
        return await guild.get_role(environ[roles[cert]])

    async def academy_handler(self, event: str, data: dict) -> dict:
        discord_user = data['discord_id']
        guild = await self.bot.fetch_guild(environ['GUILD_ID'])
        member = await guild.fetch_member(discord_user)
        if not member:
            return {"error": "User is not present in guild"}
        if event == "AccountLinked":
            roles = [r for r in [await self.get_academy_role(guild, cert['name']) for cert in data['certifications']] if r is not None]
            au_role = guild.get_role(environ['ACADEMY_ROLE'])
            roles.append(au_role)
            member.add_roles(*roles)
            return {"ok": "Added roles to user"}
        elif event == "AddCert":
            role = await self.get_academy_role(guild, data['certification']['name'])
            member.add_role(role)
            return {"ok": "Added role to user"}
        else:
            return {"error": "Unknown event"}

    @staticmethod
    def hof_role(position: int) -> Optional[int]:
        pos_top = None
        if position == 1:
            pos_top = '1'
        elif position <= 5:
            pos_top = '5'
        elif position <= 10:
            pos_top = '10'
        elif position <= 25:
            pos_top = '25'
        elif position <= 50:
            pos_top = '50'
        elif position <= 100:
            pos_top = '100'
        else:
            return None
        return RoleIDs.get_post_or_rank(pos_top)

    @staticmethod
    def vip_role(vip_level: int) -> Optional[int]:
        if vip_level == 1:
            return RoleIDs.VIP
        elif vip_level == 2:
            return RoleIDs.VIP_PLUS
        else:
            return None

    async def mp_handler(self, event: str, data: dict) -> dict:

        discord_user = data['discord_id']
        guild = await self.bot.fetch_guild(environ['GUILD_ID'])
        member = await guild.fetch_member(discord_user)
        if not member:
            return {"error": "User is not present in guild"}

        if event == "AccountLinked":
            name: str = data['name']
            await member.edit(nick=name)
            rank: str = data['rank']
            hof_pos: Optional[int] = data['hof_pos']
            vip_level: int = data['vip_level']
            machine_creator: bool  = data['machine_creator']
            challenge_creator: bool = data['challenge_creator']
            # We need to first remove conflicting roles
            to_remove = RoleIDs.ALL_POSITIONS + RoleIDs.ALL_CREATORS + RoleIDs.ALL_RANKS + [RoleIDs.VIP, RoleIDs.VIP_PLUS]
            to_assign = []
            if role := RoleIDs.get_post_or_rank(rank):
                to_assign.append(role)
            if pos := hof_pos:
                if role := WebhookCog.hof_role(pos):
                    to_assign.append(role)
            if role := WebhookCog.vip_role(vip_level):
                to_assign.append(vip_level)
            if machine_creator:
                to_assign.append(RoleIDs.BOX_CREATOR)
            if challenge_creator:
                to_assign.append(RoleIDs.CHALLENGE_CREATOR)

            to_remove = [guild.get_role(r) for r in (set(to_remove) - set(to_assign))]
            to_assign = [guild.get_role(r) for r in to_assign]
            await member.remove_roles(*to_remove)
            await member.add_roles(*to_assign)
            return {"ok": "Linked account"}

        elif event == "RankUp":
            rank = data['rank']
            rank_id: Optional[int] = RoleIDs.get_post_or_rank(rank)
            to_remove = [guild.get_role(x) for x in (set(RoleIDs.ALL_RANKS) - set([rank_id]))]
            if rank:
                member.add_roles(guild.get_role(rank_id))
            member.remove_roles(*to_remove)
            return {"ok": "Changed user rank"}
        elif event == "HofChange":
            hof_pos = data['hof_pos']
            # Random number that's way outside range in case of unranked user
            role_id = WebhookCog.hof_role(hof_pos or 10000)
            to_remove = [guild.get_role(x) for x in (set(RoleIDs.ALL_RANKS) - set([role_id]))]
            if role_id:
                member.add_roles(guild.get_role(role_id))
            member.remove_roles(*to_remove)
            return {"ok": "Changed user HOF bracket"}

        elif event == "VIPChange":
            vip_level = data['vip_level']
            role_id = WebhookCog.vip_role(vip_level)
            to_remove = [guild.get_role(x) for x in {RoleIDs.VIP, RoleIDs.VIP_PLUS} - set([role_id])]
            if role_id:
                member.add_roles(guild.get_role(role_id))
            member.remove_roles(*to_remove)
            return {"ok": "Changed user VIP role"}

        elif event == "ContentCreation":
            kind = data['kind']
            if kind == 'machine':
                member.add_roles(guild.get_role(RoleIDs.BOX_CREATOR))
            elif kind == 'challenge':
                member.add_roles(guild.get_role(RoleIDs.CHALLENGE_CREATOR))
            return {"ok": "Added content creator role"}

        else:
            return {"error": "Unknown event"}


    async def webserver(self):
        async def handler(req):
            body = await req.json()
            platforms = {"academy": academy_handler}
            return web.json_response(await platforms[body['platform']](body['event'], body['data']))

        app = web.Application()
        app.router.add_post('/', handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, '0.0.0.0', 5000)
        await self.bot.wait_until_ready()
        await self.site.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())

def setup(bot):
    cog = WebhookCog(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.webserver())

