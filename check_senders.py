#!/usr/bin/env python3

import asyncio
from aiogram.utils import markdown as md

import settings
from dispatcher import bot, db
import texts
import logging

"""
This script is running very often.
When somebody adds a new travel, in some short period
we send a message to parcel creators.
"""


async def check_senders():
    logging.info("checking senders")
    await db.init(settings.DATABASE)

    users = {}

    async def collect(travel, show_cities=False):
        user_id = travel["user_id"]
        if user_id not in users:
            users[user_id] = {}

        parcels = users[user_id]

        # that'a a parcel id, not travel id
        # for on parcel could be many travels
        pid = travel["id"]

        if pid not in parcels:
            parcel_text = texts.get_parcel_descr(travel)
            parcels[pid] = [f"\nДля посылки {parcel_text} найдены поездки:"]

        # show only ten travels max
        if len(parcels[pid]) < 10:
            parcels[pid] += [
                md.text(texts.get_sender_descr(travel, show_cities=show_cities))
            ]

            await db.add_suggestion(travel['id'], travel['travel_id'])

    travels = await db.search_travels_for_all_with_exact_cities()
    for travel in travels:
        await collect(travel)

    travels = await db.search_travels_for_all_by_countries()
    for travel in travels:
        await collect(travel, show_cities=True)

    for user_id, parcels in users.items():
        items = []
        for descr in parcels.values():
            items += descr

        footer = md.text("\nВы можете написать выбранному человеку в телеграме и договориться о передаче посылки.")
        items += [footer]
        await bot.send_message(
            user_id,
            "\n".join(items),
        )

    session = await bot.get_session()
    if session:
        await session.close()


if __name__ == "__main__":
    asyncio.run(check_senders())
