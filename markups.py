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
        'Учавствовать в диалоге',
        callback_data='start_dialog'
    ),
    types.InlineKeyboardButton(
        'Поддержать организаторов митапа',
        callback_data='donate'
    ),
]

participate_markup.add(*participate_markup_buttons)


dialog_markup = types.InlineKeyboardMarkup(row_width=2)
dialog_markup_buttons = [
    types.InlineKeyboardButton(
        'На логику диалога',
        callback_data='dialog_logic'
    ),
]

dialog_markup.add(*dialog_markup_buttons)
