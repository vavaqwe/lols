"""
Async wrapper для DEX/XT запитів - паралельна обробка для швидкості
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import time

class AsyncDEXWrapper:
    """Асинхронний wrapper для паралельних DEX запитів"""

    def __init__(self, max_concurrent=20):
        self.max_concurrent = max_concurrent
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.last_heartbeat = 0
        self.heartbeat_interval = 30

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=False)

    async def fetch_multiple_dex_prices(self, symbols: List[str], dex_client) -> Dict[str, Optional[float]]:
        """
        Паралельно отримує ціни для багатьох символів через DEX
        """
        self._log_heartbeat()

        tasks = []
        for symbol in symbols:
            task = self._fetch_single_dex_price(symbol, dex_client)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        price_map = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logging.warning(f"❌ Помилка DEX для {symbol}: {result}")
                price_map[symbol] = None
            else:
                price_map[symbol] = result

        return price_map

    async def _fetch_single_dex_price(self, symbol: str, dex_client) -> Optional[float]:
        """Отримує одну ціну DEX через thread pool"""
        try:
            loop = asyncio.get_event_loop()
            price = await loop.run_in_executor(
                self.executor,
                dex_client.get_dex_price,
                symbol,
                False  # for_convergence
            )
            return price
        except Exception as e:
            logging.warning(f"❌ DEX fetch error {symbol}: {e}")
            return None

    async def fetch_multiple_xt_prices(self, symbols: List[str], xt_client) -> Dict[str, Optional[float]]:
        """
        Паралельно отримує ціни для багатьох символів через XT
        """
        self._log_heartbeat()

        tasks = []
        for symbol in symbols:
            task = self._fetch_single_xt_price(symbol, xt_client)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        price_map = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logging.warning(f"❌ Помилка XT для {symbol}: {result}")
                price_map[symbol] = None
            else:
                price_map[symbol] = result

        return price_map

    async def _fetch_single_xt_price(self, symbol: str, xt_client) -> Optional[float]:
        """Отримує одну ціну XT через thread pool"""
        try:
            from xt_client import get_xt_price

            loop = asyncio.get_event_loop()
            price = await loop.run_in_executor(
                self.executor,
                get_xt_price,
                xt_client,
                symbol
            )
            return price
        except Exception as e:
            logging.warning(f"❌ XT fetch error {symbol}: {e}")
            return None

    def _log_heartbeat(self):
        """Логує heartbeat кожні 30 секунд"""
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            self.last_heartbeat = now
            logging.info(f"💓 Async DEX/XT heartbeat: {self.max_concurrent} concurrent workers")


# Глобальний wrapper
async_dex_wrapper = None

def get_async_wrapper(max_concurrent=20):
    """Повертає глобальний async wrapper"""
    global async_dex_wrapper
    if async_dex_wrapper is None:
        async_dex_wrapper = AsyncDEXWrapper(max_concurrent=max_concurrent)
    return async_dex_wrapper


async def batch_fetch_spreads(symbols: List[str], dex_client, xt_client) -> List[Dict]:
    """
    Паралельно отримує DEX та XT ціни для розрахунку spreads
    """
    wrapper = get_async_wrapper()

    async with wrapper:
        # Паралельно запитуємо DEX та XT
        dex_task = wrapper.fetch_multiple_dex_prices(symbols, dex_client)
        xt_task = wrapper.fetch_multiple_xt_prices(symbols, xt_client)

        dex_prices, xt_prices = await asyncio.gather(dex_task, xt_task)

    # Розраховуємо spreads
    results = []
    for symbol in symbols:
        dex_price = dex_prices.get(symbol)
        xt_price = xt_prices.get(symbol)

        if dex_price and xt_price and dex_price > 0 and xt_price > 0:
            spread = ((dex_price - xt_price) / xt_price) * 100
            results.append({
                'symbol': symbol,
                'dex_price': dex_price,
                'xt_price': xt_price,
                'spread': spread,
                'spread_abs': abs(spread)
            })

    return results
