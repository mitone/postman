from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import markdown as md
from aiogram.types import (
    ParseMode,
    Message,
    CallbackQuery,
)
from aiogram.dispatcher import FSMContext
from datetime import date, datetime

import settings
from dispatcher import bot, dp, db
import markups
import texts
import common


class ParcelForm(StatesGroup):
    start = State()
    city_src = State()
    city_dest = State()
    date_end_year = State()
    date_end_month = State()
    date_end_day = State()
    parcel_type = State()


async def new_parcel(message: Message, state: FSMContext):
    """Start process of creating a new parcel.
    Set the state to first field in ParcelForm. If user doesn't have
    any parcels we don't show him a choices (with edit and etc) and start
    to enter the parcel details right away.
    """
    await state.reset_data()

    count = await db.get_user_parcels_count(state.user)
    await db.add_event(message.from_user.id, message.from_user.username, "parcel")

    if count > 0:
        await ParcelForm.start.set()
        text, markup = markups.get_parcel_start_markup()
        await message.reply(text, reply_markup=markup)
    else:
        await ParcelForm.city_src.set()
        await message.answer(
            md.bold(texts.PARCEL_ENTER),
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN,
        )
        await message.answer(texts.CITY_SRC, reply_markup=None)


async def change_parcel(parcel_id: int, state: FSMContext, message: Message):
    parcel = await db.get_parcel(parcel_id, state.user)
    text, markup = markups.get_parcel_change_markup()

    async with state.proxy() as data:
        data["parcel_id"] = parcel_id
        prev_message_id = data.get("prev_message_id")
        data["prev_message_id"] = message.message_id
        data["cleanup_message_id"] = data["prev_message_id"]

    if prev_message_id:
        await bot.delete_message(state.chat, prev_message_id)

    await message.edit_text(
        md.text(
            md.text(texts.get_parcel_descr(parcel)),
            "",
            text,
            sep="\n",
        ),
        reply_markup=markup,
    )


async def search_parcel(parcel_id: int, state: FSMContext, message: Message):
    """Search travels by specified parcel"""

    parcel = await db.get_parcel(parcel_id, state.user)
    descr = texts.get_parcel_descr(parcel)

    await message.edit_text(f"Ищем отправителя по дате {descr}")
    senders = await search_sender(message, parcel_id, by_countries=parcel["search_by_countries"])

    if not senders:
        

    await state.finish()


@dp.callback_query_handler(Text(equals="parcel_add"), state=ParcelForm.start)
async def parcel_add_callback(query: CallbackQuery, state: FSMContext):
    count = await db.get_user_parcels_count(state.user)

    if count >= settings.MAX_PARCELS_PER_USER:
        await query.answer(
            f"Активных посылок не должно быть больше {settings.MAX_PARCELS_PER_USER}"
        )
        return

    await ParcelForm.city_src.set()
    await query.message.edit_text(
        md.bold(texts.PARCEL_ENTER), reply_markup=None, parse_mode=ParseMode.MARKDOWN
    )
    await query.message.answer(texts.CITY_SRC, reply_markup=None)


@dp.callback_query_handler(Text(equals="parcel_correct"), state=ParcelForm.start)
async def parcel_correct_callback(query: CallbackQuery, state: FSMContext):
    """User wants to change parcels.
    If there is only one - show edit form for it.
    If more - allow to make a choice
    """
    rows = await db.get_user_parcels(state.user)
    if len(rows) == 0:
        await query.answer(texts.PARCEL_RECORDS_EMPTY)
    elif len(rows) == 1:
        parcel_id = rows[0]["id"]
        await change_parcel(parcel_id, state, query.message)
    else:
        async with state.proxy() as data:
            # if edit will be canceled, this will cleanup buttons
            data["cleanup_message_id"] = query.message.message_id

        text, markup = markups.get_parcels_markup(rows, "parcel_correct")
        await query.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(Text(equals="parcel_search"), state=ParcelForm.start)
async def parcel_search_callback(query: CallbackQuery, state: FSMContext):
    rows = await db.get_user_parcels(state.user)
    if len(rows) == 0:
        await query.answer(texts.PARCEL_RECORDS_EMPTY)
    elif len(rows) == 1:
        parcel_id = rows[0]["id"]
        await search_parcel(parcel_id, state, query.message)
    else:
        text, markup = markups.get_parcels_markup(rows, "parcel_search")
        await query.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(Text(equals="parcel_done"), state=ParcelForm.start)
async def parcel_done_callback(query: CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text(texts.SAVED, reply_markup=None)


@dp.callback_query_handler(Text(equals="add_search_by_countries"), state='*')
async def add_search_by_countries(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if "parcel_id" in data:
            await db.change_parcel(
                data["parcel_id"], state.user, "search_by_countries", True
            )
            await query.answer("Добавлен поиск по странам")

            if "parcel_destination_msg_id" in data:
                message_id = data["parcel_destination_msg_id"]
                text = data["parcel_destination_text"] + " (также по странам)"

                await bot.edit_message_text(
                    text,
                    state.chat,
                    message_id,
                    reply_markup=None,
                    parse_mode=ParseMode.MARKDOWN,
                )

                del data["parcel_destination_msg_id"]
                del data["parcel_destination_text"]
        else:
            await query.answer("error")

        await state.finish()
        await query.message.delete()


@dp.callback_query_handler(Text(startswith="parcel_correct##"), state=ParcelForm.start)
async def parcel_correct_callback_by_id(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    async with state.proxy() as data:
        data["parcel_id"] = parcel_id

    await change_parcel(parcel_id, state, query.message)


@dp.callback_query_handler(Text(startswith="parcel_recheck_found##"))
async def parcel_recheck_found(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    await db.change_parcel(parcel_id, state.user, "active", False)
    await query.message.edit_text(texts.PARCEL_PRE_DONATE_MSG)
    await common.show_donate(query.message)


@dp.callback_query_handler(Text(startswith="parcel_recheck_notfound##"))
async def parcel_recheck_not_found(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    await db.change_parcel(parcel_id, state.user, "active", False)
    await query.message.edit_text(texts.PARCEL_PRE_DONATE_NOT_FOUND)
    await common.show_donate(query.message)


@dp.callback_query_handler(Text(startswith="parcel_recheck_search##"))
async def parcel_recheck_search(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    await search_parcel(parcel_id, state, query.message)


@dp.callback_query_handler(Text(startswith="parcel_recheck_nolook##"))
async def parcel_recheck_nolook(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    await db.change_parcel(parcel_id, state.user, "active", False)
    await query.message.edit_text(texts.PARCEL_PRE_DONATE_NOT_FOUND)


@dp.callback_query_handler(Text(startswith="parcel_search##"), state=ParcelForm.start)
async def parcel_search_callback_by_id(query: CallbackQuery, state: FSMContext):
    parcel_id = int(query.data.split("##")[1])
    await search_parcel(parcel_id, state, query.message)


@dp.callback_query_handler(Text(equals="parcel_delete"), state=ParcelForm.start)
async def parcel_delete(query: CallbackQuery, state: FSMContext):
    parcel_id = None
    async with state.proxy() as data:
        try:
            parcel_id = data["parcel_id"]
        except:
            await query.answer("invalid id")

    if parcel_id is not None:
        await db.delete_parcel(parcel_id, state.user)
        await query.message.edit_text(texts.PARCEL_DELETED)

    await state.finish()


async def parcel_city_dst_selected(message, state, city_id, city_name, edit=False):
    """Dest city has been selected.
    If a new parcel - show the next step
    If editing - show the editing form
    """

    parcel_id = None
    async with state.proxy() as data:
        data["city_dst_id"] = city_id
        data["city_dst"] = city_name
        city_src = data.get("city_src")

        parcel_id = data.get("parcel_id")

    if parcel_id is not None:
        # update db
        await db.change_parcel(parcel_id, state.user, "city_dst", int(city_id))

        # show the editing form
        await ParcelForm.start.set()
        await change_parcel(parcel_id, state, message)
    else:
        await ParcelForm.next()

        text = md.text(
            md.bold("Ищется посылка из "),
            md.underline(city_src),
            md.bold(" в "),
            md.underline(city_name),
        )

        if edit:
            msg = await message.edit_text(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg = await message.reply(
                text,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )

        # we will save the message id and text, and if user select search
        # by countries we will change it
        if msg:
            async with state.proxy() as data:
                data["parcel_destination_msg_id"] = msg["message_id"]
                data["parcel_destination_text"] = text

        await common.ask_for_date(message, texts.PARCEL_DATE_END)


async def parcel_city_selected(message, state, city_id, city_name, edit=False):
    """City has been selected.
    If a new parcel - show the next step
    If editing - show the editing form
    """

    parcel_id = None
    async with state.proxy() as data:
        if "city_src_id" in data:
            # redirect to city dst handler
            await parcel_city_dst_selected(
                message, state, city_id, city_name, edit=edit
            )
            return

        data["city_src_id"] = city_id
        data["city_src"] = city_name
        parcel_id = data.get("parcel_id")

    if parcel_id is not None:
        # that's editing mode
        # update field in database
        await db.change_parcel(parcel_id, state.user, "city_src", int(city_id))

        # editing form
        await ParcelForm.start.set()
        await change_parcel(parcel_id, state, message)
    else:
        text = md.bold("Город отправления: " + city_name)
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

        # next field and ask for dest city
        await ParcelForm.next()
        await message.answer(texts.CITY_DEST, reply_markup=None)


@dp.message_handler(state=ParcelForm.city_src)
@dp.message_handler(state=ParcelForm.city_dest)
async def show_parcel_city(message: Message, state: FSMContext):
    """
    In previous message user entered a text with city name.
    Now show him a list of cities that apply to searching city.
    Or if it's only one just select it and go to the next field.
    """
    city = await common.show_cities(message, state)
    if city is not None:
        await parcel_city_selected(message, state, city["id"], city["name"])


# Departing city has been selected
@dp.callback_query_handler(state=ParcelForm.city_src)
async def process_parcel_city_src(query: CallbackQuery, state: FSMContext):
    """Process a query callback after user click a button with the city name"""
    try:
        city_id, city_name = query.data.split("#")
        assert city_id
        assert city_name
    except:
        await query.answer("invalid city")
        return

    await parcel_city_selected(query.message, state, city_id, city_name, edit=True)


@dp.callback_query_handler(state=ParcelForm.city_dest)
async def process_parcel_city_dst(query: CallbackQuery, state: FSMContext):
    """User clicked on a button with dest city"""

    try:
        city_id, city_name = query.data.split("#")
        assert city_id
        assert city_name
    except:
        await query.answer("invalid city")
        return

    await parcel_city_dst_selected(query.message, state, city_id, city_name, edit=True)


@dp.callback_query_handler(state=ParcelForm.date_end_year)
async def process_parcel_year_end(query: CallbackQuery, state: FSMContext):
    """User clicked on a button with a year"""

    await common.process_year(query, state, ParcelForm)


@dp.callback_query_handler(state=ParcelForm.date_end_month)
async def process_parcel_month_end(query: CallbackQuery, state: FSMContext):
    """User clicked on a button with a month"""

    await common.process_month(query, state, ParcelForm)


@dp.callback_query_handler(state=ParcelForm.date_end_day)
async def process_parcel_day_end(query: CallbackQuery, state: FSMContext):
    """User clicked on a button with a day"""

    try:
        day = int(query.data)
    except ValueError:
        await query.answer("invalid day")
        return

    parcel_id = None
    async with state.proxy() as data:
        date_end = date(data["year"], data["month"], day)
        data["date_end"] = str(date_end)
        parcel_id = data.get("parcel_id")

    if parcel_id is None:
        dt = date_end.strftime("%d.%m.%Y")
        await query.message.edit_text(
            md.bold("Дата по которую нужно искать: " + dt),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await ParcelForm.parcel_type.set()
        await common.ask_for_parcel_type(query.message)
    else:
        await db.change_parcel(parcel_id, state.user, "date_end", date_end)
        await ParcelForm.start.set()
        await change_parcel(parcel_id, state, query.message)


@dp.callback_query_handler(
    Text(equals="parcel_change_city_src"), state=ParcelForm.start
)
async def parcel_change_city_src(query: CallbackQuery, state: FSMContext):
    """Changing a parcel. Ask for a city name"""

    await ParcelForm.city_src.set()
    await query.message.answer(texts.CITY_SRC, reply_markup=None)


@dp.callback_query_handler(
    Text(equals="parcel_change_city_dest"), state=ParcelForm.start
)
async def parcel_change_city_dest(query: CallbackQuery, state: FSMContext):
    """Changing a parcel. Ask for a dest city name"""

    await ParcelForm.city_dest.set()
    await query.message.answer(texts.CITY_DEST, reply_markup=None)


@dp.callback_query_handler(
    Text(equals="parcel_change_date_end"), state=ParcelForm.start
)
async def parcel_change_date_end(query: CallbackQuery, state: FSMContext):
    await ParcelForm.date_end_year.set()
    await common.ask_for_date(query.message, texts.PARCEL_DATE_END)


@dp.callback_query_handler(
    Text(equals="parcel_change_parcel_type"), state=ParcelForm.start
)
async def parcel_change_parcel_type(query: CallbackQuery, state: FSMContext):
    await ParcelForm.parcel_type.set()
    await common.ask_for_parcel_type(query.message)


async def search_sender(message: Message, parcel_id: int, by_countries=False):
    """Search senders for specified parcel_id"""

    if by_countries:
        rows = await db.search_travels_by_parcel_on_countries(parcel_id)

        print(rows)
    else:
        rows = await db.search_travels_by_parcel(parcel_id)

    if len(rows) == 0:
        return False
    else:
        descr = [texts.PARCEL_FOUND]
        descr += [
            md.text(texts.get_sender_descr(sender, show_cities=by_countries))
            for sender in rows
        ]

        await message.answer("\n".join(descr), parse_mode=ParseMode.MARKDOWN)
        for sender in rows:
            await db.add_suggestion(parcel_id, sender["id"])

    return True




@dp.callback_query_handler(state=ParcelForm.parcel_type)
async def process_parcel_type(query: CallbackQuery, state: FSMContext):
    """
    After selecting the parcel type we save a full parcel (or show a form if it's
    editing)
    After saving try to search if there is a matching travels.
    Also ask if user needs searching on countries level.
    """

    parcel_id = None
    created_id = 0

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
        parcel_id = data.get("parcel_id")


        сountry_src = data['city_src'].split('/')[0]
        country_dst = data['city_dst'].split('/')[0]

        print(сountry_src, country_dst)

        if is_ready and parcel_id is None:
            created_id = await db.new_parcel(
                int(data["city_src_id"]),
                int(data["city_dst_id"]),
                datetime.strptime(data["date_end"], "%Y-%m-%d").date(),
                data["parcel_type"],
                data["user_id"],
                data["user_username"],
            )


    if is_ready:
        # used selected 'Ready' (Готово)
        if parcel_id is None:
            # it's a new parcel
            await query.message.edit_text(
                md.bold(f"Тип посылки: {name.lower()}"),
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )

            # save
            dest_msg_id = data.get("parcel_destination_msg_id")
            dest_msg_text = data.get("parcel_destination_text")

            await state.finish()
            await query.answer(texts.PARCEL_SAVED)

            # try to search
            senders = await search_sender(query.message, created_id)
            print(senders, senders == False)

            if not senders:
                if сountry_src == country_dst:
                    await search_sender(query.message, created_id, by_countries=True)

                else:
                    text, markup = markups.get_search_by_countries_markup()
                    await query.message.answer(
                        text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN
                    )

            # ask if user wants to search by countries
            async with state.proxy() as data:
                data["parcel_id"] = created_id

                # restore
                data["parcel_destination_msg_id"] = dest_msg_id
                data["parcel_destination_text"] = dest_msg_text



        else:
            # it's editing, just show the form
            await db.change_parcel(parcel_id, state.user, "parcel_type", selected_types)
            await ParcelForm.start.set()
            await change_parcel(parcel_id, state, query.message)
    else:
        # still selecting a parcel type
        add_ready = len(selected_types) > 0
        choose_text, markup = markups.get_parcel_types_markup(
            add_ready=add_ready, selected=selected_types
        )
        text = md.text(
            md.bold(f"Выбрано: {name.lower()}"),
            choose_text,
            sep="\n",
        )
        await query.message.edit_text(
            text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN
        )
