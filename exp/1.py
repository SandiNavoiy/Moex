import asyncio

import aiohttp

import aiomoex
import pandas as pd


async def main():
    async with aiohttp.ClientSession() as session:
        data = await aiomoex.get_board_history(session, 'SNGSP')
        df = pd.DataFrame(data)
        df.set_index('TRADEDATE', inplace=True)
        print(df.head(), '\n')
        print(df.tail(), '\n')
        df.info()


asyncio.run(main())