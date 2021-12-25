from dataclasses import dataclass
from datetime import datetime, date
from typing import Union

from discord import Embed
from discord.ext import commands
from discord.commands import Option
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.noahbot import bot
from src.conf import SlashPerms, PrefixPerms, GUILD_ID, MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.cmds._proxy_helpers import Reply, get_user_id


@dataclass
class Note:
    id: int
    user_id: str
    note: str
    date: date
    moderator: str


@dataclass
class Infraction:
    id: int
    user_id: str
    reason: str
    weight: int
    moderator: str
    date: date


def name():
    return 'history'


def description():
    return 'Print the infraction history and basic details about the Discord user.'


async def perform_action(ctx: ApplicationContext, reply, user_id):
    left = False
    user_id = get_user_id(user_id)
    if user_id is None:
        await reply(ctx, 'Error: malformed user ID.')
        return

    member = ctx.guild.get_member(int(user_id))
    if member is None:
        member = await bot.fetch_user(user_id)
        left = True

    today_date = datetime.date(datetime.now())

    notes = get_notes_of(user_id)
    infractions = get_infractions_for(user_id)

    expired_infractions = 0
    active_infractions = 0

    if infractions is not None:
        for inf in infractions:
            diff = inf.date - today_date
            if diff.days >= -14:
                active_infractions = active_infractions + 1
            else:
                expired_infractions = expired_infractions + 1

    if left:
        join_date = 'Left'
    else:
        join_date = join_date = member.joined_at.date()

    creation_date = member.created_at.date()
    strike_value = 0
    for infraction in infractions:
        strike_value += infraction.weight

    summary_text = f"""
**{member.name}**
Total infraction(s): **{len(infractions)}**
Expired: **{expired_infractions}**
Active: **{len(infractions) - expired_infractions}**
Current strike value: **{strike_value}/3**
Join date: **{join_date}**
Creation Date: **{creation_date}**
"""
    if strike_value >= 3:
        summary_text += f"\n**Review needed** by Sr. Mod or Admin: **{strike_value}/3 strikes**."

    embed = Embed(title="Summary", description=f"{summary_text}", color=0x115599)
    _embed_titles_of(embed, entry_type='infractions', history_entries=infractions, today_date=today_date, entry_handler=produce_inf_text)
    _embed_titles_of(embed, entry_type='notes', history_entries=notes, today_date=today_date, entry_handler=produce_note_text)

    if len(embed) > 6000:
        await ctx.send(content=f'History embed is too big to send ({len(embed)}/6000 allowed chars).')
    else:
        # await ctx.send(embed=embed)
        await reply(ctx, embed=embed)


def get_notes_of(user_id: Union[str, int]):
    notes = []
    with connect(host=MYSQL_HOST, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT * FROM user_note WHERE user_id = %s"""
            cursor.execute(query_str, (user_id, ))
            for row in cursor.fetchall():
                # row = id, user_id, note, date, moderator
                notes.append(Note(row[0], row[1], row[2], row[3], row[4]))

    return notes


def get_infractions_for(user_id: Union[str, int]):
    infractions = []
    with connect(host=MYSQL_HOST, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """SELECT * FROM infraction_record WHERE user_id = %s"""
            cursor.execute(query_str, (user_id, ))
            for row in cursor.fetchall():
                # row = id, user_id, reason, weight, date, moderator
                infractions.append(Infraction(row[0], row[1], row[2], row[3], row[4], row[5]))

    return infractions


def _embed_titles_of(embed, entry_type: str, history_entries, today_date, entry_handler):
    """
    Generic producer of "title" fields for provided "embed", containing the "entry_handler" formatted text of the
    "entry_type" object representation. In plain english, this generates the text for the embed which works the same
    way regardless of if the text is an infraction, a note or something third.
    Important: this function mutates the provided "embed"!
    """
    entry_records = [[]]
    if history_entries is not None:
        current_row = 0
        for entry in history_entries:
            entry_text = entry_handler(entry, today_date=today_date)

            if sum(len(r) for r in entry_records[current_row]) + len(entry_text) > 1000:
                entry_records.append(list())
                current_row += 1
            entry_records[current_row].append(entry_text)

    if len(entry_records[0]) == 0:
        embed.add_field(name=f"{entry_type.capitalize()}", value=f'No {entry_type.lower()}.', inline=False)
    else:
        for i in range(0, len(entry_records)):
            embed.add_field(
                name=f"{entry_type.capitalize()} ({i + 1}/{len(entry_records)})",
                value='\n\n'.join(entry_records[i]),
                inline=False
            )


def produce_note_text(note, today_date):
    """ Produces a single note line in the embed containing basic information about the note and the note itself."""
    return f"#{note.id} by <@{note.moderator}> on {note.date}: " \
           f"{note.note if len(note.note) <= 300 else note.note[:300] + '...'}"


def produce_inf_text(infraction, today_date):
    """ Produces a formatted block of text of an infraction, containing all relevant information."""
    diff = infraction.date - today_date
    if diff.days >= -14:
        expired_status = "Active"
    else:
        expired_status = "Expired"
    return f"""#{infraction.id}, weight: {infraction.weight}
Issued by <@{infraction.moderator}> on {infraction.date} ({expired_status}):
{infraction.reason if len(infraction.reason) <= 300 else infraction.reason[:300] + '...'}"""


@bot.slash_command(guild_ids=[GUILD_ID], permissions=[SlashPerms.ADMIN, SlashPerms.MODERATOR], name=name(), description=description())
async def action_slash(ctx: ApplicationContext, user_id: Option(str, 'User ID or @mention name.')):
    await perform_action(ctx, Reply.slash, user_id)


@commands.command(name=name(), help=description())
@commands.has_any_role(*(PrefixPerms.ALL_ADMINS + PrefixPerms.ALL_MODS))
async def action_prefix(ctx: ApplicationContext, user_id):
    await perform_action(ctx, Reply.prefix, user_id)


def setup(le_bot):
    le_bot.add_command(action_prefix)
