import asyncio
from datetime import datetime
from typing import Coroutine

from src.log4noah import STDOUT_LOG


async def schedule(task: Coroutine, run_at: datetime):
    """
    Schedule an "Awaitable" for future execution, i.e. an async function.

    For example to schedule foo(1, 2) 421337 seconds into the future:
    await schedule(foo(1, 2), at=(dt.datetime.now() + dt.timedelta(seconds=421337)))
    """
    now = datetime.now()
    if run_at < now:
        STDOUT_LOG.debug(f'Target execution is in the past. Setting sleep timer to 0.', target_exec=repr(run_at), current_time=repr(now))
        seconds = 0
    else:
        seconds = int((run_at - now).total_seconds())
        STDOUT_LOG.debug(f'Task {task.__name__} will run after {seconds} seconds.', target_exec=repr(run_at), current_time=repr(now))

    await asyncio.sleep(seconds)
    return await task
