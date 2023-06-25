from aiogram import types

client_start_markup = types.InlineKeyboardMarkup(row_width=2)
client_start_markup_buttons = [
    types.InlineKeyboardButton(
        'О боте',
        callback_data='about_bot'
    ),
    types.InlineKeyboardButton(
        'Принять участье в митапе',
        callback_data='participate_in_meetup'
    ),
]

client_start_markup.add(*client_start_markup_buttons)


participate_markup = types.InlineKeyboardMarkup(row_width=2)
participate_markup_buttons = [
    types.InlineKeyboardButton(
        'Программа мероприятия',
        callback_data='schedule'
    ),
    types.InlineKeyboardButton(
        'Задать вопрос спикеру',
        callback_data='ask_question'
    ),
    types.InlineKeyboardButton(
        'Хочу познакомиться!',
        callback_data='start_dialog'
    ),
    types.InlineKeyboardButton(
        'Поддержать организаторов митапа',
        callback_data='donate'
    ),
]

participate_markup.add(*participate_markup_buttons)


organizer_markup = types.InlineKeyboardMarkup(row_width=2)
additional_organizer_buttons = [
    types.InlineKeyboardButton(
        'Общее оповещение',
        callback_data='anounce'
    ),
    types.InlineKeyboardButton(
        'Закончить выступление спикера',
        callback_data='next_presentation'
    ),
]
organizer_markup.add(*participate_markup_buttons)
organizer_markup.add(*additional_organizer_buttons)


dialog_markup = types.InlineKeyboardMarkup(row_width=2)
dialog_markup_buttons = [
    types.InlineKeyboardButton(
        'Давай попробуем',
        callback_data='dialog_logic'
    ),
    types.InlineKeyboardButton(
        'Не хочу',
        callback_data='participate_in_meetup'
    ),

]

dialog_markup.add(*dialog_markup_buttons)


form_markup = types.InlineKeyboardMarkup(row_width=2)
form_markup_buttons = [
    types.InlineKeyboardButton(
        'Подобрать другую',
        callback_data='repeat_form'
    ),
]

form_markup.add(*form_markup_buttons)
