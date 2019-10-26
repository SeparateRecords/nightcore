from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any, Union

from nightcore.effect import nightcore as nc

if TYPE_CHECKING:
    from os import PathLike
    from pydub import AudioSegment
    from nightcore.change import RelativeChange


async def nightcore(
    audio: Union[AudioSegment, PathLike],
    amount: Union[RelativeChange, float],
    **kwargs: Any,
) -> AudioSegment:
    """Async function equivalent to `nightcore.nightcore`, for asyncio"""
    loop = asyncio.get_running_loop()
    func = functools.partial(nc, audio, amount, **kwargs)
    audio = await loop.run_in_executor(None, func)
    return audio
