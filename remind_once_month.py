#!/usr/bin/env python3

import asyncio

import settings
from dispatcher import bot, db
import markups
import logging


async def remind():
    logging.info("remind_once_month")
    await db.init(settings.DATABASE)

    rows = await db.get_contacts_by_parcels()
    for row in rows:
        text, markup = markups.get_reminds_markup()
        await bot.send_message(row["user_id"], text, reply_markup=markup)

    session = await bot.get_session()
    if session:
        await session.close()


if __name__ == "__main__":
    asyncio.run(remind())
