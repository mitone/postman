from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    ParseMode,
)
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from dispatcher import bot, dp, db

from aiogram.utils.exceptions import MessageToDeleteNotFound

import markups
import texts
import common


@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
@dp.message_handler(state="*", commands="cancel")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    markup = ReplyKeyboardRemove()
    if current_state is None:
        await message.reply("Нет текущего действия для отмены", reply_markup=markup)
        return
    else:
        async with state.proxy() as data:
            if 'cleanup_message_id' in data:
                msg_id = data['cleanup_message_id']
                del data['cleanup_message_id']

                try:
                    await bot.delete_message(state.chat, msg_id)
                except MessageToDeleteNotFound as e:
                    print('Exception: ', e)
                    return

    await state.finish()
    await message.reply("Отменено", reply_markup=markup)


@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    # await db.add_event(message.from_user.id, message.from_user.username, 'start')
    await message.reply(
        texts.START,
        reply_markup=markups.get_start_markup(),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(commands=["donate"])
async def donate(message: Message):
    await common.show_donate(message)


@dp.message_handler(commands=["about"])
async def about(message: Message):
    await db.add_event(message.from_user.id, message.from_user.username, 'about')
    await message.answer(texts.DESCRIPTION, parse_mode=ParseMode.MARKDOWN)
