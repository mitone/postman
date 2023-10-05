from aiogram.types import (
    ParseMode,
    Message,
    CallbackQuery,
)
from aiogram.dispatcher import FSMContext
from datetime import date
import markups
from dispatcher import db
import texts
import settings


async def ask_for_travel_duration(message: Message):
    """Ask travel frequency after cities"""

    text, markup = markups.get_travel_duration_markup()

    await message.answer(
        text, 
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def ask_for_date(message: Message, text: str):
    """Show buttons with years, this starts a date selection"""

    await message.answer(
        text,
        reply_markup=markups.get_years_markup(date.today()),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def ask_for_parcel_type(message: Message):
    """Show buttons with parcel types"""

    text, markup = markups.get_parcel_types_markup()
    await message.answer(
        text,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def set_parcel_type(state, parcel_type):
    """User selected some parcel type, add it to the selected list"""

    async with state.proxy() as data:
        # we have to use a list, since to redis it goes as json
        pt = data.get("parcel_type", [])
        if parcel_type in pt:
            pt.remove(parcel_type)
        else:
            pt.append(parcel_type)

        data["parcel_type"] = pt


async def ask_for_payment_type(message: Message):
    """Show buttons with payment types"""

    text, markup = markups.get_payment_types_markup()
    await message.answer(text, reply_markup=markup)


async def show_cities(message: Message, state: FSMContext):
    """Search the city and show buttons with cities (if found)"""

    detail = texts.CITY_DETAIL
    markup = None

    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
        data["user_username"] = message.from_user.username

    rows = await db.search_city(message.text)
    if len(rows) == 1:
        # we found an exact match, just return the found city
        row = rows[0]
        return {"id": row[0], "name": row[1]}

    elif len(rows) > 10:
        detail = texts.CITY_TOO_MANY
    elif len(rows) == 0:
        detail = texts.CITY_NO
    else:
        markup = markups.get_cities_markup(rows)

    await message.reply(detail, reply_markup=markup)


async def process_year(query: CallbackQuery, state: FSMContext, form):
    """User selected the year, show buttons with months"""

    try:
        year = int(query.data)
    except ValueError:
        await query.answer("invalid year")
        return

    async with state.proxy() as data:
        data["year"] = year

    await form.next()

    today = date.today()
    from_month = today.month if today.year == year else 1
    await query.message.edit_text(
        "Выберите месяц:",
        reply_markup=markups.get_months_markup(from_month),
    )


async def process_month(query: CallbackQuery, state: FSMContext, form):
    """User selected a month, show buttons with days"""

    try:
        month = int(query.data)
    except ValueError:
        await query.answer("invalid month")
        return

    async with state.proxy() as data:
        data["month"] = month
        year = data["year"]

    await form.next()

    today = date.today()
    if year == today.year and month == today.month:
        from_day = today.day
    else:
        from_day = 1

    await query.message.edit_text(
        "Выберите день:",
        reply_markup=markups.get_dates_markup(year, month, from_day),
    )


async def show_donate(message: Message):
    """Show the donate text and QR code with payment information"""

    await db.add_event(message.from_user.id, message.from_user.username, "donate")
    await message.answer_photo(
        settings.QR_CODE_FILE_ID,
        texts.DONATE_TEXT,
        parse_mode=ParseMode.MARKDOWN,
    )
