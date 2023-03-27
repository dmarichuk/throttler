import asyncio
import time
from collections import deque
from typing import Union, Callable, Optional


class Throttler:
    """
    Context manager for limiting rate of accessing to context block.

    Example usages:
        - https://github.com/uburuntu/throttler/blob/master/examples/example_throttlers.py
        - https://github.com/uburuntu/throttler/blob/master/examples/example_throttlers_aiohttp.py
    """
    __slots__ = ('_rate_limit', '_period', '_times', '_throttle_cb')

    def __init__(
        self, 
        rate_limit: int, 
        period: Union[int, float] = 1.0, 
        throttle_cb: Optional[Callable] = None):
        if not (isinstance(rate_limit, int) and rate_limit > 0):
            raise ValueError('`rate_limit` should be positive integer')

        if not (isinstance(period, (int, float)) and period > 0.):
            raise ValueError('`period` should be positive float')

        if throttle_cb and not (isinstance(throttle_cb, Callable)):
            raise ValueError('`throttle_cb` should be callable')

        self._rate_limit = float(rate_limit)
        self._period = float(period)
        self._throttle_cb = throttle_cb

        self._times = deque(0. for _ in range(rate_limit))

    async def __aenter__(self):
        while True:
            curr_ts = time.monotonic()
            diff = curr_ts - (self._times[0] + self._period)
            if diff > 0.:
                self._times.popleft()
                break
            if self._throttle_cb:
                return await self._throttle_cb()
            await asyncio.sleep(-diff)

        self._times.append(curr_ts)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
