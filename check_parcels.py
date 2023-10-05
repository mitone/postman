#!/usr/bin/env python3

import asyncio
from datetime import datetime, timedelta

import settings
from dispatcher import bot, db
import markups
import logging


async def check_parcels():
    ''' Скрипт через 24 часа после оставления посылки спрашивает как дела '''

    logging.info("checking parcels")
    await db.init(settings.DATABASE)

    await db.set_parcels_unactive()
    rows = await db.get_parcels(datetime.now() - timedelta(hours=24))
    for row in rows:
        text, markup = markups.get_parcel_results_markup(row)
        await bot.send_message(row["user_id"], text, reply_markup=markup)
        await db.mark_parcel_notified(row["id"], row["user_id"])

    session = await bot.get_session()
    if session:
        await session.close()


if __name__ == "__main__":
    asyncio.run(check_parcels())
