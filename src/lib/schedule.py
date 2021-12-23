import asyncio
from datetime import datetime
from typing import Awaitable, TypeVar


T = TypeVar("T")


async def schedule(task: Awaitable[T], at: datetime) -> T:
    """
    Schedule an "Awaitable" for future execution, i.e. an async function.

    For example to schedule foo(1, 2) 421337 seconds into the future:
    await schedule(foo(1, 2), at=(dt.datetime.now() + dt.timedelta(seconds=421337)))
    """
    now = datetime.now()

    if at < now:
        seconds = 0
    else:
        seconds = (at - now).seconds

    await asyncio.sleep(seconds)
    return await task
