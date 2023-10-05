import calendar, locale
import texts
import functools
import datetime

from aiogram.types import (
    InlineKeyboardMarkup,
    BotCommand,
    InlineKeyboardButton,
)

BotCommands = [
    BotCommand("travel", texts.READY),
    BotCommand("parcel", texts.LOOKING),
    BotCommand("cancel", texts.CANCEL),
    BotCommand("about", texts.ABOUT),
    BotCommand("donate", texts.DONATE),
    BotCommand("feedback", texts.FEEDBACK),
]


# change locale for Russian
try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except:
    pass

@functools.lru_cache()
def get_months_markup(from_month=1):
    months_markup = InlineKeyboardMarkup(row_width=4)

    for i in range(from_month, 13):
        months_markup.insert(
            InlineKeyboardButton(text=calendar.month_name[i], callback_data=str(i))
        )

    return months_markup


@functools.lru_cache()
def get_dates_markup(year: int, month: int, from_day=1):
    cal = calendar.Calendar()
    markup = InlineKeyboardMarkup(row_width=6)
    for i in cal.itermonthdays(year, month):
        if i < from_day:
            continue

        markup.insert(InlineKeyboardButton(text=str(i), callback_data=str(i)))

    return markup


@functools.lru_cache()
def get_start_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    for text, callback_data in texts.START_CHOICE:
        markup.insert(InlineKeyboardButton(text=text, callback_data=callback_data))
    return markup


@functools.lru_cache()
def get_cancel_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(
        InlineKeyboardButton(text='Продолжить',
                             callback_data='/continue')
    )
    markup.insert(
        InlineKeyboardButton(text='Отменить',
                             callback_data='/cancel')
    )

    return markup


def gen_by_choices(choices, text_in_callback=False, row_width=1, selected=[]):
    markup = InlineKeyboardMarkup(row_width=row_width)
    for text, callback in choices:
        if text_in_callback:
            callback_data = callback + "##" + text
        else:
            callback_data = callback

        if callback in selected:
            text = '☑️ ' + text

        markup.insert(InlineKeyboardButton(text=text, callback_data=callback_data))

    return markup


@functools.lru_cache()
def get_reminds_markup():
    return (
        texts.REMIND_TEXT,
        gen_by_choices(texts.REMIND_CHOICES, False),
    )


@functools.lru_cache()
def get_travel_start_markup():
    return (
        texts.TRAVEL_CHOOSE,
        gen_by_choices(texts.TRAVEL_CHOICE_1, False),
    )


@functools.lru_cache()
def get_parcel_start_markup():
    return (
        texts.PARCEL_CHOOSE,
        gen_by_choices(texts.PARCEL_CHOICE_BEGIN, False),
    )


def get_cities_markup(rows):
    markup = InlineKeyboardMarkup(row_width=2)
    for row in rows:
        markup.insert(
            InlineKeyboardButton(
                text=row[1], callback_data=str(row[0]) + "#" + row[1]
            )
        )

    return markup

@functools.lru_cache()
def get_travel_duration_markup():

    return (
        texts.TRAVEL_DURATION,
        gen_by_choices(texts.TRAVEL_DURATION_CHOICE, False),
    )


@functools.lru_cache()
def get_years_markup(today):
    markup = InlineKeyboardMarkup(row_width=2)

    until_year = today.year
    if today > datetime.date(today.year, 10, 1):
        until_year = today.year + 1

    for year in range(today.year, until_year + 1):
        markup.insert(InlineKeyboardButton(text=str(year), callback_data=str(year)))

    return markup


def get_parcel_types_markup(selected=[], add_ready=False):
    markup = gen_by_choices(texts.PARCEL_TYPES, True,
                                    row_width=2,
                                    selected=selected)
    if add_ready:
        markup.insert(
            InlineKeyboardMarkup(text="✅ Готово", callback_data="ready##")
        )

    return (texts.PARCEL_TYPE_CHOOSE, markup)


@functools.lru_cache()
def get_payment_types_markup():
    return (
        texts.PAYMENT_TYPE_CHOOSE,
        gen_by_choices(texts.PAYMENT_TYPES, True),
    )

@functools.lru_cache()
def get_search_by_countries_markup():
    return (
        texts.PARCEL_SEARCH_BY_COUNTRIES,
        gen_by_choices(texts.PARCEL_SEARCH_BY_COUNTRIES_CHOICES, False),
    )

@functools.lru_cache()
def get_travel_change_markup():
    return (
        texts.TRAVEL_SELECT_CHANGE,
        gen_by_choices(texts.TRAVEL_CHOICE_2, row_width=2),
    )


@functools.lru_cache()
def get_parcel_change_markup():
    return (
        texts.PARCEL_SELECT_CHANGE,
        gen_by_choices(texts.PARCEL_CHANGE_ITEMS, row_width=2),
    )


def get_travels_markup(rows):
    markup = InlineKeyboardMarkup(row_width=1)
    for row in rows:
        dt = texts.REGULAR_TRAVELS_TEXT
        if row["travel_date"]:
            dt = row["travel_date"].strftime("%d.%m.%Y")
        callback = f"travel_correct##{row['id']}"
        text = f"{dt}: из {row['from']} в {row['to']}"
        btn = InlineKeyboardButton(text=text, callback_data=callback)
        markup.insert(btn)

    return texts.TRAVEL_SELECT, markup


def get_parcels_markup(rows, callback_prefix):
    markup = InlineKeyboardMarkup(row_width=1)
    for row in rows:
        dt_end = row["date_end"].strftime("%d.%m.%Y")
        callback = f"{callback_prefix}##{row['id']}"
        text = f"По дате {dt_end}: из {row['from']} в {row['to']}"
        btn = InlineKeyboardButton(text=text, callback_data=callback)
        markup.insert(btn)

    return texts.PARCEL_SELECT, markup


@functools.lru_cache()
def get_travel_results_markup():
    return (
        texts.TRAVEL_CHECK,
        gen_by_choices(texts.TRAVEL_CHOICE_3, row_width=1),
    )


@functools.lru_cache()
def get_parcel_results_markup(parcel):
    markup = InlineKeyboardMarkup(row_width=1)
    descr = texts.get_parcel_descr(parcel)
    msg_text = texts.PARCEL_RECHECK % descr
    for text, callback_prefix in texts.PARCEL_RECHECK_CHOICE:
        callback = f"{callback_prefix}##{parcel['id']}"
        btn = InlineKeyboardButton(text=text, callback_data=callback)
        markup.insert(btn)

    return (
        msg_text,
        markup,
    )
