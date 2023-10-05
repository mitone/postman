from aiogram.utils import markdown as md

PROJECT_NAME = "ПЕРЕДАМ"
START = f"""
Привет, это {PROJECT_NAME}👋

✈️ *Летите и готовы передать посылку?*
Заполните данные своей поездки, и вам напишут люди, которым вы могли бы помочь передать посылку.

🚨 *Нужно срочно передать посылку?*
Заполните информацию, и бот направит список подходящих поездок по интересующему маршруту.

🤝 При удачном мэтче, вы сможете списаться в телеграме и договориться о деталях. Передача может быть платной или бесплатной, в зависимости от ваших договоренностей.

🍒 Подписывайтесь на [телеграм-канал бота](https://t.me/peredam_channel)

🍩 Бот полностью бесплатный, работает за донаты.
"""
DONATE_TEXT = """
Наша миссия - сделать передачу посылок между любыми точками мира максимально удобной и быстрой.

Вы можете поддержать проект ПЕРЕДАМ, переведя комфортную для вас сумму по [ссылке](https://pay.cloudtips.ru/p/f323ed5c) или QR-коду.

Спасибо 😊
"""

CHOOSE_ACTION = "Выберите действие "
CANCEL = "Отмена текущего действия"
DONATE = "Задонатить"
FEEDBACK = "Обратная связь"
NOT_IMPLEMENTED = "Не реализовано"
FIRST_CANCEL = "Сначала завершите прошлое действие (или отмените из меню)"
SAVED = "Все изменения сохранены"
FEEDBACK_TEXT = """
По любым вопросам с ботом пишите в @peredam_support
"""

READY = "Лечу и готов передать"
LOOKING = "Нужно передать посылку"
ABOUT = "Подробнее о сервисе"
START_CHOICE = (
    (LOOKING, "/new_parcel"),
    (READY, "/new_travel"),
    (ABOUT, "/about"),
)
DESCRIPTION = f"""
*Что мы делаем?*

🌍 {PROJECT_NAME}- это площадка мэтчинга людей для быстрой передачи посылок по всему миру.

Площадка выполняет две функции:

 - собирает информацию о рейсах и людях, которые готовы передать посылки
 - выдает контактную информацию (телеграм-ник и дату рейса) **только** людям, которые запрашивают ваш маршрут. Никто другой контактов не увидит😎

❗️ℹ️ Мы оказываем только информационные услуги, помогаем людям найти друг друга.

*Кому мы будем полезны?*

{PROJECT_NAME} будет полезен людям, которым нужно срочно передать посылку 🚨. Курьерская служба не всегда является решением: или будут везти долго ⏳, или крайне дорого 💴, или же они в целом не возьмут посылку (в случае документов и лекарств) 🚫. В таких ситуациях люди ищут попутчика.
Также, множество людей сами вызываются помочь передать что-то в другой город. Кто-то делает это по доброте душевной 🫶, кто-то таким образом окупает часть стоимости билета💰.
И те, и другие размещают информацию о своих поездках и посылках в многочисленных чатах😩. Мы хотим облегчить эту задачу и собрать всех людей на одной площадке. Тогда поиск будет занимать не часы, а всего 5 минут 🤩.

*Зачем мы это делаем?*

🚀 🌍 Наша миссия - сделать передачу посылок между любыми точками мира максимально удобной и быстрой. Для этого мы расширяем охват путешественников и улучшаем сервис, чтобы люди чаще использовали ПЕРЕДАМ.

*Как вы можете помочь?*

📣 делиться информацией о сервисе со своими знакомыми
✈️ каждый раз вносить информацию о вашей поездке в {PROJECT_NAME}
🍩 по возможности, задонатить, чтобы мы частично окупили издержки
😉 делиться своим мнение и предложениями по доработке {PROJECT_NAME} (""" + md.escape_md("через @peredam_support") + ")"

SEARCH_CHOOSE = "Выберите, что требуется"
SEARCH_CHOICE_1 = (
    ("Разместить объявление о посылке", "search_add"),
    ("Проверить существующую посылку", "search_check"),
    ("Скорретировать посылку", "search_correct"),
)

TRAVEL_START = "Создание поездки"
TRAVEL_CHOOSE = "Рады, что вы готовы помочь людям. Что хотите сделать?"
TRAVEL_CHOICE_1 = (
    ("Разместить новую поездку", "travel_add"),
    ("Внести корректировки в поездку", "travel_correct"),
    ("Отмена", "travel_done"),
)
TRAVEL_CHOICE_2 = (
    ("Город отправления", "travel_change_city_src"),
    ("Город назначения", "travel_change_city_dest"),
    ("Дата поездки", "travel_change_travel_date"),
    ("Тип посылки", "travel_change_parcel_type"),
    ("Тип оплаты", "travel_change_payment_type"),
    ("⚱️  Удалить поездку", "travel_delete"),
    ("◀️ Выйти из режима редактирования", "travel_done"),
)

TRAVEL_DURATION_CHOICE = (
    ("Разовая", "travel_duration_onetime"),
    ("Езжу регулярно", "travel_duration_regular"),
)

REGULAR_TRAVELS_TEXT = "Регулярные поездки"

TRAVEL_CHECK = "Как прошла поездка?"
TRAVEL_CHECK_SORRY = f"Жаль, будем ждать новых поездок на {PROJECT_NAME}"
TRAVEL_CHECK_SORRY_2 = f"Жаль, будем ждать ваших поездок на {PROJECT_NAME}"
TRAVEL_CHOICE_3 = (
    ("Нашлись  посылки, удалось передать!", "/donate"),
    ("Не нашлось посылок", "/sorry_and_donate"),
    ("Поездка не состоялась", "/just_sorry"),
)

TRAVEL_ENTER = "Введите информацию о поездке:"
TRAVEL_SELECT = "Выберите поездку:"
TRAVEL_SELECT_CHANGE = "Выберите пункт, который необходимо изменить в поездке"

TRAVEL_EMPRY_RECORDS = "У вас нет активных поездок"
TRAVEL_DELETED = "Поездка успешно удалена. Бот больше не будет показывать кому-то эту поездку."
TRAVEL_SAVED = "🎉 Ура! Бот сохранил данные выше. Сейчас от вас больше ничего не требуется. Бот поделится вашим никнеймом с теми, кому будет нужна ваша помощь, и они сами напишут вам."

CITY_SRC = "Город отправления (введите текст для поиска): "
CITY_DETAIL = "Выберите город: "
CITY_TOO_MANY = "Слишком много результатов. Попробуйте уточнить название города или ввести точное название города на английском"
CITY_DEST = "Город назначения (введите текст для поиска): "
CITY_NO = "Город не найден. Попробуйте уточнить название города"
TRAVEL_DURATION = "Поездка разовая или регулярная"
TRAVEL_DATE = "Выбор даты поездки"

PARCEL_SELECT = "Выберите посылку:"
PARCEL_SELECT_CHANGE = "Выберите пункт, который необходимо изменить в посылке"

PARCEL_TYPE_CHOOSE = "Выберите все типы посылок, которые готовы передать \(можно несколько\):"
PARCEL_TYPES = (
    ("Документы", "docs"),
    ("Лекарства", "farmacy"),
    ("Что-то небольшое", "small"),
    ("Багаж", "baggage"),
)

PARCEL_TYPES_DICT = {}
for text, val in PARCEL_TYPES:
    PARCEL_TYPES_DICT[val] = text


def get_parcel_type_name(types):
    names = []
    for t in types:
        names.append(PARCEL_TYPES_DICT[t])
    return ", ".join(names)


PAYMENT_TYPE_CHOOSE = "Выберите тип оплаты:"
PAYMENT_TYPES = (
    ("За вознаграждение", "money"),
    ("За карму 🙏", "karma"),
)

PARCEL_CHOOSE = "Выберите что требуется: "
PARCEL_CHOICE_BEGIN = (
    ("Разместить объявление о посылке", "parcel_add"),
    ("Проверить существующую посылку", "parcel_search"),
    ("Скорректировать посылку", "parcel_correct"),
    ("Отмена", "parcel_done"),
)
PARCEL_ENTER = "Введите информацию о посылке"
PARCEL_DATE_END = "По какую дату искать поездку"
PARCEL_DELETED = "Посылка успешно удалена"

PARCEL_CHANGE_ITEMS = (
    ("Город отправления", "parcel_change_city_src"),
    ("Город назначения", "parcel_change_city_dest"),
    (PARCEL_DATE_END, "parcel_change_date_end"),
    ("Типы посылки", "parcel_change_parcel_type"),
    ("⚱️  Удалить посылку", "parcel_delete"),
    ("Добавить поиск по странам", "add_search_by_countries"),
    ("◀️ Выйти из режима редактирования", "parcel_done"),
)

PARCEL_SEARCH_BY_COUNTRIES = "Подписаться на поиск по странам? Покажем курьеров, чьи поездки совпадают по странам. Это расширит поиск, если вы готовы передать посылку внутри страны. "
PARCEL_SEARCH_BY_COUNTRIES_CHOICES = (
    ("Добавить поиск по странам", "add_search_by_countries"),
    ("Оставить поиск по городам", "/delete_message"),
)

PARCEL_SEARCH_BY_COUNTRIES_TEXT = """
Расширили поиск. Напишем, как найдем курьера.
"""
PARCEL_NOT_FOUND = """
К сожалению, сейчас на площадке нет подходящих поездок. Бот сохранил данные выше и сразу пришлет подходящую поездку, как только появится 🙏
"""
PARCEL_FOUND = """
Вот список подходящих поездок с контактами. Вы можете написать им в телеграме и договориться о передаче посылки:
"""
PARCEL_RECHECK = """
Недавно вы оставляли заказ на передачу посылки:
%s
Расскажите, как дела?
"""
PARCEL_PRE_DONATE_MSG = """
Мы рады, что смогли помочь вам
"""
PARCEL_PRE_DONATE_NOT_FOUND = """
Спасибо, что воспользовались ПЕРЕДАМ. Будем рады видеть вас снова
"""

PARCEL_RECHECK_CHOICE = (
    (f"Нашли человека в {PROJECT_NAME}", "parcel_recheck_found"),
    (f"Нашли человека не в {PROJECT_NAME}", "parcel_recheck_notfound"),
    ("Не нашли человека, ещё ищем", "parcel_recheck_search"),
    ("Не нашли человека, больше не ищем", "parcel_recheck_nolook"),
)

PARCEL_RECORDS_EMPTY = "Сейчас у вас нет активных посылок. Вы можете создать новую."
PARCEL_SAVED = "Посылка успешно сохранена"

ANALYTICS = {
    "start": "Открыл бота",
    "travel": "Меню поездка",
    "parcel": "Меню посылка",
    "about": "Меню о боте",
    "donate": "Меню донат",
    "feedback": "Меню обратная связь",
}

REMIND_TEXT = """
Привет, это ПЕРЕДАМ 👋
Подскажите, есть ли у вас в ближайших планах поездки?
Если так, внесите данные о ней в бот и помогите кому-то передать посылку.
"""

REMIND_CHOICES = (
    ("Пока никуда не собираюсь", "/see_you"),
    ("Еду и готов помочь", "/new_travel"),
)

SEE_YOU = "Спасибо, до новых встреч!"

PAYMENT_TYPES_DICT = {}
for text, val in PAYMENT_TYPES:
    PAYMENT_TYPES_DICT[val] = text

# Construct full description of travel from the database
def get_travel_descr(travel):
    dt = REGULAR_TRAVELS_TEXT

    if travel["travel_date"]:
        dt = travel["travel_date"].strftime("%d.%m.%Y")

    payment_type = PAYMENT_TYPES_DICT[travel["payment_type"]]

    parcel_types = []
    for t in travel["parcel_type"]:
        parcel_types.append(PARCEL_TYPES_DICT[t])

    parcel_type = ", ".join(parcel_types)
    text = f"{dt}: из {travel['from']} в {travel['to']}\n{parcel_type.lower()}\n{payment_type.lower()}"

    return text


# Construct full description of parcel from the database
def get_parcel_descr(parcel):
    dt_end = parcel["date_end"].strftime("%d.%m.%Y")

    parcel_types = []
    if "parcel_type" in parcel:
        for t in parcel["parcel_type"]:
            parcel_types.append(PARCEL_TYPES_DICT[t])

    text = f"{dt_end}: из {parcel['from']} в {parcel['to']}"
    if len(parcel_types):
        parcel_type = ", ".join(parcel_types)
        text += f"\n{parcel_type.lower()}"

    return text


def get_sender_descr(sender, show_cities=False):
    ''' Construct description of sender '''
    dt = REGULAR_TRAVELS_TEXT

    if sender["travel_date"]:
        dt = sender["travel_date"].strftime("%d.%m.%Y")

    payment_type = PAYMENT_TYPES_DICT[sender["payment_type"]]

    parcel_types = []
    if "parcel_type" in sender:
        for t in sender["parcel_type"]:
            parcel_types.append(PARCEL_TYPES_DICT[t])

    loc = ""
    if show_cities:
        loc = f" из {sender['travel_from']} в {sender['travel_to']}"

    text = f"<b>{dt}{loc}</b>: @{sender['user_username']} - {payment_type.lower()}"
    if len(parcel_types):
        parcel_type = ", ".join(parcel_types)
        text += f", тип посылки: {parcel_type.lower()}"

    return text
