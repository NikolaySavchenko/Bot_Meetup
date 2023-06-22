import asyncio
import logging
import os
from pathlib import Path

import django
import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types.message import ContentType
from asgiref.sync import sync_to_async

logging.basicConfig(level=logging.INFO)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

from meetup_bot.models import Member
import markups as m


BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(Path(BASE_DIR, '.env'))
token = os.environ['BOT_TOKEN']
PAYMENT_TOKEN = os.environ['PAYMENT_TOKEN']



bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



class UserState(StatesGroup):
    meetup = State()


@dp.message_handler()
async def start_conversation(msg: types.Message, state: FSMContext):
    member, created = await sync_to_async(Member.objects.get_or_create)(telegram_id=msg.from_id)
    if not created:
        message = f'Приветствую, {member.telegram_name}'
    await msg.answer(message)
    await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text='about_bot')
async def about_bot(cb: types.callback_query):
    message = 'Информация о боте + информация о ближайшем митапе'
    await cb.message.answer(message)
    await cb.message.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text='participate_in_meetup', state=[UserState, None])
async def participate(cb: types.callback_query):
    member = await sync_to_async(Member.objects.get)(telegram_id=cb['from']['id'])
    if member.role == 'organizer':
        organizer_markup = m.participate_markup
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
        organizer_markup.add(*additional_organizer_buttons)
        await cb.message.answer('Organizer menu', reply_markup=organizer_markup)
    else:
        await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='anounce', state=[UserState, None])
async def anounce(cb: types.callback_query):
    message = 'Заглушка для anounce'
    await cb.message.answer(message)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='next_presentation', state=[UserState, None])
async def next_presentation(cb: types.callback_query):
    message = 'Заглушка для next_presentation'
    await cb.message.answer(message)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='schedule', state=[UserState, None])
async def show_schedule(cb: types.callback_query):
    message = 'Заглушка для расписания'
    await cb.message.answer(message)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='ask_question', state=[UserState, None])
async def ask_question(cb: types.callback_query):
    message = 'Заглушка на вопрос, надо будет перепроверить на перехват cb.message.text'
    await cb.message.answer(message)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='start_dialog', state=[UserState, None])
async def start_dialog(cb: types.callback_query):
    message = 'FAQ для диалога'
    await cb.message.answer(message)
    await cb.message.answer('Dialog menu', reply_markup=m.dialog_markup)


@dp.callback_query_handler(text='donate', state=[UserState, None])
async def make_donation(cb: types.CallbackQuery, state: FSMContext):
    txt = 'заглушка для сообщения при донате'
    price = types.LabeledPrice(
        label=txt,
        amount=100 * 100
    )
    await bot.send_invoice(
        cb.message.chat.id,
        title=txt,
        description=txt,
        provider_token=PAYMENT_TOKEN,
        currency='rub',
        photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[price],
        start_parameter='test',
        payload='test-invoice-payload'
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(
        content_types=ContentType.SUCCESSFUL_PAYMENT,
        state=[UserState, None]
    )
async def successful_payment(message: types.Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        f'Payment at {message.successful_payment.total_amount // 100}'
        f'{message.successful_payment.currency} done'
    )
    # тут фунция для записи в бд информации о донате await sync_to_async(funcs.pay_order)(payloads['schedule_id'])



executor.start_polling(dp, skip_updates=False)
