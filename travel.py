#!/usr/bin/env python3

import settings
import texts

from aiogram.types import (
    ParseMode,
    Message,
    CallbackQuery,
)
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import markdown as md

from datetime import date, datetime
from dispatcher import bot, dp, db

import markups
import common


#TODO: use cancel_msg
class TravelForm(StatesGroup):
    start = State()
    city_src = State()
    city_dest = State()
    travel_duration = State()
    date_year = State()
    date_month = State()
    date_day = State()
    parcel_type = State()
    payment_type = State()


async def new_travel(message: Message, state: FSMContext):
    await state.reset_data()

    count = await db.get_user_travels_count(state.user)
    await db.add_event(message.from_user.id, message.from_user.username, 'travel')

    if count > 0:
        text, markup = markups.get_travel_start_markup()
        await TravelForm.start.set()
        await message.reply(text, reply_markup=markup)
    else:
        await TravelForm.city_src.set()
        await message.answer(
            md.bold(texts.TRAVEL_ENTER), reply_markup=None, parse_mode=ParseMode.MARKDOWN
        )
        await message.answer(texts.CITY_SRC, reply_markup=None)


async def change_travel(travel_id: int, state: FSMContext, message: Message):
    travel = await db.get_travel(travel_id, state.user)
    text, markup = markups.get_travel_change_markup()

    async with state.proxy() as data:
        prev_message_id = data.get("prev_message_id")
        data["prev_message_id"] = message.message_id
        data["travel_id"] = travel_id
        data["cleanup_message_id"] = message.message_id

    if prev_message_id:
        await bot.delete_message(state.chat, prev_message_id)

    await message.edit_text(
        md.text(
            md.text(texts.get_travel_descr(travel)),
            "",
            text,
            sep="\n",
        ),
        reply_markup=markup,
    )



@dp.callback_query_handler(Text(startswith="travel_add"), state=TravelForm.start)
async def travel_add_callback(query: CallbackQuery, state: FSMContext):
    if not query.message.from_user.username:
        await query.answer(
            f"Для добавления поездки должен быть установлен ник для связи."
        )
        return

    count = await db.get_user_travels_count(state.user)

    if count >= settings.MAX_TRAVELS_PER_USER:
        await query.answer(
            f"Активных поездок не должно быть больше {settings.MAX_TRAVELS_PER_USER}"
        )
        return

    await TravelForm.city_src.set()
    await query.message.edit_text(
        md.bold(texts.TRAVEL_ENTER), reply_markup=None, parse_mode=ParseMode.MARKDOWN
    )
    await query.message.answer(texts.CITY_SRC, reply_markup=None)


@dp.callback_query_handler(Text(equals="travel_correct"), state=TravelForm.start)
async def travel_correct_callback(query: CallbackQuery, state: FSMContext):
    ''' Show travels list or go to editing form if only one '''

    rows = await db.get_user_travels(state.user)

    if len(rows) == 0:
        await query.answer(texts.TRAVEL_EMPRY_RECORDS)
    elif len(rows) == 1:
        travel_id = rows[0]["id"]
        await change_travel(travel_id, state, query.message)
    else:
        async with state.proxy() as data:
            # if edit will be canceled, this will cleanup buttons
            data["cleanup_message_id"] = query.message.message_id

        text, markup = markups.get_travels_markup(rows)
        await query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)




@dp.callback_query_handler(Text(equals="travel_done"), state=TravelForm.start)
async def travel_done_callback(query: CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text(texts.SAVED, reply_markup=None)


@dp.callback_query_handler(Text(startswith="travel_correct##"), state=TravelForm.start)
async def travel_correct_callback_by_id(query: CallbackQuery, state: FSMContext):
    travel_id = int(query.data.split("##")[1])
    await change_travel(travel_id, state, query.message)


@dp.callback_query_handler(Text(equals="travel_delete"), state=TravelForm.start)
async def travel_delete(query: CallbackQuery, state: FSMContext):
    travel_id = None
    async with state.proxy() as data:
        try:
            travel_id = data["travel_id"]
        except:
            await query.answer("invalid id")

    if travel_id is not None:
        await db.delete_travel(travel_id, state.user)
        await query.message.edit_text(texts.TRAVEL_DELETED)

    await state.finish()


@dp.callback_query_handler(
    Text(equals="travel_change_city_src"), state=TravelForm.start
)
async def travel_change_city_src(query: CallbackQuery, state: FSMContext):
    await TravelForm.city_src.set()
    await query.message.answer(texts.CITY_SRC, reply_markup=None)


@dp.callback_query_handler(
    Text(equals="travel_change_city_dest"), state=TravelForm.start
)
async def travel_change_city_dest(query: CallbackQuery, state: FSMContext):
    await TravelForm.city_dest.set()
    await query.message.answer(texts.CITY_DEST, reply_markup=None)


@dp.callback_query_handler(
    Text(equals="travel_change_travel_date"), state=TravelForm.start
)
async def travel_change_travel_date(query: CallbackQuery, state: FSMContext):
    await TravelForm.date_year.set()
    await common.ask_for_date(query.message, texts.TRAVEL_DATE)

""" Обработчик кнопки регулярной поездки """
@dp.callback_query_handler(
    Text(equals="travel_duration_regular"), state=TravelForm.travel_duration
)
async def travel_duration_regular(query: CallbackQuery, state: FSMContext):
    travel_id = None

    async with state.proxy() as data:
        name = "за вознаграждение"
        payment_type = "money"
        parcel_type = {"docs", "small", "farmacy", "baggage"}
        date = None
        travel_id = data.get("travel_id")

        date = data.get("date")

        if date:
            date = datetime.strptime(data["date"], "%Y-%m-%d").date(),

        if travel_id is None:
            await db.new_travel(
                int(data["city_src_id"]),
                int(data["city_dst_id"]),
                date,
                parcel_type,
                payment_type,
                data["user_id"],
                data["user_username"],
            )

            await db.new_travel(
                int(data["city_dst_id"]),
                int(data["city_src_id"]),
                date,
                parcel_type,
                payment_type,
                data["user_id"],
                data["user_username"],
            )


    if travel_id is None:

        # text = md.text(md.bold(f"Оплата: {name}Тип посылки: документы, небольшое, лекарства, багаж"))

        parcel_type = "документы, что-то небольшое, лекарства, багаж"

        text = md.text(
            md.bold("\nВыбранная дата: "),
            "регулярные поездки",
            md.bold("\nТип посылки: "),
            parcel_type,
            md.bold(f"\nОплата: "),
            name
        )

        await query.message.edit_text(
            text,
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN,
        )

        await state.finish()
        await query.answer(texts.TRAVEL_SAVED)
        await query.message.answer(
            texts.TRAVEL_SAVED,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await db.change_travel(travel_id, state.user, "payment_type", payment_type)
        await TravelForm.start.set()
        await change_travel(travel_id, state, query.message)




""" Обработчик кнопки разовой поездки """
@dp.callback_query_handler(
    Text(equals="travel_duration_onetime"), state=TravelForm.travel_duration
)
async def travel_duration_onetime(query: CallbackQuery, state: FSMContext):
    await TravelForm.next()
    await common.ask_for_date(query.message, texts.TRAVEL_DATE)



@dp.callback_query_handler(
    Text(equals="travel_change_parcel_type"), state=TravelForm.start
)
async def travel_change_parcel_type(query: CallbackQuery, state: FSMContext):
    await TravelForm.parcel_type.set()
    await common.ask_for_parcel_type(query.message)


@dp.callback_query_handler(
    Text(equals="travel_change_payment_type"), state=TravelForm.start
)
async def travel_change_payment_type(query: CallbackQuery, state: FSMContext):
    await TravelForm.payment_type.set()
    await common.ask_for_payment_type(query.message)


async def travel_city_dst_selected(message, state, city_id, city_name, edit=False):
    travel_id = None
    async with state.proxy() as data:
        data["city_dst_id"] = city_id
        data["city_dst"] = city_name
        city_src = data.get("city_src")

        travel_id = data.get("travel_id")

    if travel_id is not None:
        await db.change_travel_city_dest(travel_id, state.user, int(city_id))
        await TravelForm.start.set()
        await change_travel(travel_id, state, message)
    else:
        await TravelForm.next()
        text = md.text(
                md.bold("Поездка из "),
                md.underline(city_src),
                md.bold(" в "),
                md.underline(city_name),
            )

        if edit:
            await message.edit_text(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.reply(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )

        await common.ask_for_travel_duration(message)


async def travel_city_selected(message, state, city_id, city_name, edit=False):
    """
    City has been selected.
    If a new travel - show the next step
    If editing - show the editing form
    """

    travel_id = None
    async with state.proxy() as data:
        if "city_src_id" in data:
            # redirect to city dst handler
            await travel_city_dst_selected(
                message, state, city_id, city_name, edit=edit
            )
            return

        data["city_src_id"] = city_id
        data["city_src"] = city_name
        travel_id = data.get("travel_id")

    if travel_id is not None:
        await db.change_travel_city_src(travel_id, state.user, int(city_id))
        await TravelForm.start.set()
        await change_travel(travel_id, state, message)
    else:
        text = md.bold("Город отправления: " + city_name)
        await TravelForm.next()
        if edit:
            await message.edit_text(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.reply(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )

        await message.answer(texts.CITY_DEST, reply_markup=None)

@dp.message_handler(state=TravelForm.city_src)
@dp.message_handler(state=TravelForm.city_dest)
async def show_travel_city(message: Message, state: FSMContext):
    city = await common.show_cities(message, state)
    if city is not None:
        await travel_city_selected(message, state, city["id"], city["name"])


@dp.callback_query_handler(state=TravelForm.city_src)
async def process_travel_city_src(query: CallbackQuery, state: FSMContext):
    ''' Departing city has been selected '''

    try:
        city_id, city_name = query.data.split("#")
        assert city_id
        assert city_name
    except:
        await query.answer("invalid city")
        return

    await travel_city_selected(query.message, state, city_id, city_name, edit=True)


@dp.callback_query_handler(state=TravelForm.city_dest)
async def process_travel_city_dst(query: CallbackQuery, state: FSMContext):
    ''' Destination city has been selected '''

    try:
        city_id, city_name = query.data.split("#")
        assert city_id
        assert city_name
    except ValueError:
        await query.answer("invalid city")
        return

    await travel_city_dst_selected(query.message, state, city_id, city_name, edit=True)


# @dp.callback_query_handler(state=TravelForm.travel_option)
# async def process_travel_option(query: CallbackQuery, state: FSMContext):
#     await common.process_travel_option(query, state, TravelForm)


@dp.callback_query_handler(state=TravelForm.date_year)
async def process_travel_year(query: CallbackQuery, state: FSMContext):
    await common.process_year(query, state, TravelForm)


@dp.callback_query_handler(state=TravelForm.date_month)
async def process_travel_month(query: CallbackQuery, state: FSMContext):
    await common.process_month(query, state, TravelForm)


@dp.callback_query_handler(state=TravelForm.date_day)
async def process_travel_day(query: CallbackQuery, state: FSMContext):
    try:
        day = int(query.data)
    except ValueError:
        await query.answer("invalid day")
        return

    travel_id = None
    async with state.proxy() as data:
        travel_date = date(data["year"], data["month"], day)
        data["date"] = str(travel_date)
        travel_id = data.get("travel_id")

    if travel_id is None:
        dt = travel_date.strftime("%d.%m.%Y")
        await query.message.edit_text(
            md.bold("Выбранная дата: " + dt),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await TravelForm.parcel_type.set()
        await common.ask_for_parcel_type(query.message)
    else:
        await db.change_travel(travel_id, state.user, "travel_date", travel_date)
        await TravelForm.start.set()
        await change_travel(travel_id, state, query.message)


@dp.callback_query_handler(state=TravelForm.parcel_type)
async def process_parcel_type(query: CallbackQuery, state: FSMContext):
    travel_id = None

    try:
        parcel_type, _ = query.data.split("##")
    except:
        await query.answer("Редактирование: тип посылки не выбран")
        return

    is_ready = parcel_type == "ready"

    if not is_ready:
        await common.set_parcel_type(state, parcel_type)

    async with state.proxy() as data:
        selected_types = data["parcel_type"]
        name = texts.get_parcel_type_name(selected_types)
        travel_id = data.get("travel_id")

    if is_ready:
        if travel_id is None:
            await query.message.edit_text(
                md.bold(f"Тип посылки: {name.lower()}"),
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            await TravelForm.payment_type.set()
            await common.ask_for_payment_type(query.message)
        else:
            await db.change_travel(
                travel_id, state.user, "parcel_type", selected_types
            )
            await TravelForm.start.set()
            await change_travel(travel_id, state, query.message)
    else:
        add_ready = len(selected_types) > 0
        choose_text, markup = markups.get_parcel_types_markup(
                add_ready=add_ready,
                selected=selected_types)
        text = md.text(
            md.bold(f"Выбрано: {name.lower()}"),
            choose_text,
            sep="\n",
        )
        await query.message.edit_text(
            text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN_V2
        )


@dp.callback_query_handler(state=TravelForm.payment_type)
async def process_payment_type(query: CallbackQuery, state: FSMContext):
    travel_id = None

    async with state.proxy() as data:
        payment_type, name = query.data.split("##")
        data["payment_type"] = payment_type
        data["payment_type_name"] = name
        travel_id = data.get("travel_id")
        date = data.get("date")

        if date:
            date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        if travel_id is None:
            await db.new_travel(
                int(data["city_src_id"]),
                int(data["city_dst_id"]),
                date,
                data["parcel_type"],
                data["payment_type"],
                data["user_id"],
                data["user_username"],
            )

    if travel_id is None:
        await query.message.edit_text(
            md.bold(f"Оплата: {name.lower()}"),
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN,
        )

        await state.finish()
        await query.answer(texts.TRAVEL_SAVED)
        await query.message.answer(
            texts.TRAVEL_SAVED,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await db.change_travel(travel_id, state.user, "payment_type", payment_type)
        await TravelForm.start.set()
        await change_travel(travel_id, state, query.message)
