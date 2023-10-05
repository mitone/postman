#!/usr/bin/env python3

import asyncio
from datetime import date, timedelta

import settings
from dispatcher import bot, db
import markups
import logging


async def check_travels():
    logging.info("travels script: send a message how travel went and make unactive")

    await db.init(settings.DATABASE)

    rows = await db.get_travels(date.today() - timedelta(days=1))
    text, markup = markups.get_travel_results_markup()
    for row in rows:
        await bot.send_message(row["user_id"], text, reply_markup=markup)
        await db.change_travel(row["id"], row["user_id"], "active", False)

    session = await bot.get_session()
    if session:
        await session.close()


if __name__ == "__main__":
    asyncio.run(check_travels())
