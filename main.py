#!/usr/bin/env python3

import aiogram
import settings
import texts
import traceback

from aiogram.types import (
    Message,
    CallbackQuery,
    ContentType,
)
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils import markdown as md
from aiogram.types import ChatMemberUpdated

from dispatcher import dp, db, bot
from markups import BotCommands

# order is important here
from base_handlers import *
from travel import new_travel, TravelForm
from parcel import new_parcel, ParcelForm


@dp.callback_query_handler(Text(startswith="/"))
async def handle_command_callback(query: CallbackQuery, state: FSMContext):
    if query.data == "/new_travel":
        await query.answer(texts.CHOOSE_ACTION)
        await new_travel(query.message, state)
    elif query.data == "/new_parcel":
        await query.answer(texts.CHOOSE_ACTION)
        await new_parcel(query.message, state)
    elif query.data == "/about":
        await query.answer("")
        await about(query.message)
    elif query.data == "/donate":
        await query.answer("")
        await query.message.edit_text(query.message.text, reply_markup=None)
        await donate(query.message)
    elif query.data == "/sorry_and_donate":
        await query.answer("")
        await query.message.edit_text(query.message.text, reply_markup=None)
        await query.message.reply(texts.TRAVEL_CHECK_SORRY)
        await query.message.answer(texts.DONATE_TEXT)
    elif query.data == "/just_sorry":
        await query.answer("")
        await query.message.edit_text(query.message.text, reply_markup=None)
        await query.message.reply(texts.TRAVEL_CHECK_SORRY_2)
    elif query.data == "/see_you":
        await query.answer("")
        await query.message.edit_text(query.message.text, reply_markup=None)
        await query.message.answer(texts.SEE_YOU)
    elif query.data == "/delete_message":
        await bot.delete_message(state.chat, query.message.message_id)
    else:
        await query.answer(texts.NOT_IMPLEMENTED)


@dp.message_handler(commands=["feedback"])
async def handle_feedback(message: Message):
    await message.answer(texts.FEEDBACK_TEXT)


@dp.message_handler(commands=["travel"])
async def handle_new_travel(message: Message, state: FSMContext):
    await new_travel(message, state)


@dp.message_handler(content_types=ContentType.PHOTO)
async def handler_qr(message: Message):
    if len(message.photo):
        await message.answer(message.photo[0].file_id)


@dp.message_handler(commands=["parcel"])
async def handle_new_parcel(message: Message, state: FSMContext):
    await new_parcel(message, state)

@dp.my_chat_member_handler()
async def handle_chat_member_updated(member: ChatMemberUpdated):
    print("Updated", member)


async def on_startup(dispatcher, url=None, cert=None):
    bot = dispatcher.bot

    await bot.set_chat_menu_button(menu_button=aiogram.types.MenuButtonCommands())
    await bot.set_my_commands(BotCommands)

    
    print('database', settings.DATABASE)
    await db.init(settings.DATABASE)


@dp.message_handler(state=TravelForm)
@dp.message_handler(state=ParcelForm)
async def handle_other(message: Message):
    await message.reply(texts.FIRST_CANCEL)


@dp.errors_handler(exception=aiogram.exceptions.MessageNotModified)
async def handle_message_not_modified(update, error):
    return True


@dp.errors_handler()
async def handle_errors(update: aiogram.types.Update, error):
    #await bot.send_message(update.message.from_user.id,
    #    "Произошла ошибка во время работы формы")

    await bot.send_message(
        settings.ADMIN_ID,
        md.text(
            md.code(str(update)),
            md.bold(str(error)),
            md.code("".join(traceback.format_exception(error))),
            sep="\n",
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return True


if __name__ == "__main__":
    aiogram.executor.start_polling(
        dp,
        on_startup=on_startup,
        skip_updates=settings.DEBUG,
        timeout=60,
        allowed_updates=["message", "callback_query"],
    )
