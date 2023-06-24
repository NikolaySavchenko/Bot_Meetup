import asyncio
import logging
import os
import random
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

from meetup_bot.models import Member, Form
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
    name = State()
    age = State()
    company = State()
    job = State()
    stack = State()
    hobby = State()
    goal = State()
    region = State()


@dp.message_handler()
async def start_conversation(msg: types.Message, state: FSMContext):
    if msg['from']['username']:
        member, created = await sync_to_async(Member.objects.get_or_create)(telegram_id=msg.from_id,
                                                                            telegram_name=msg['from']['username'])
    else:
        member, created = await sync_to_async(Member.objects.get_or_create)(telegram_id=msg.from_id)
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


def get_random_form(member):
    forms = Form.objects.exclude(member=member)
    try:
        random_user = random.choice(forms)

        text = f'Имя: {random_user.name} \n\
                 Возраст: {random_user.age} \n\
                 Должность и компания: {random_user.job}, {random_user.company} \n\
                 Технологии: {random_user.stack} \n\
                 Хобби: {random_user.hobby} \n\
                 Цель: {random_user.goal} \n\
                 Регион: {random_user.region} \n\
                 Телеграмм: @{random_user.member.telegram_name}'
    except IndexError:
        pass
        text = "Никто еще не прошел опрос. Ты первый."

    return text


@dp.callback_query_handler(text='start_dialog', state=[UserState, None])
async def start_dialog(cb: types.callback_query):
    member = await sync_to_async(Member.objects.get)(telegram_id=cb['from']['id'])
    forms = await sync_to_async(Form.objects.filter)(member=member)
    form_exists = await sync_to_async(forms.exists)()

    if not form_exists:
        await cb.message.answer('Хочешь найти новые контакты?\
        Тогда пройди опрос и я пришлю тебе анкету единомышленника.\
        Если он тебе не понравится, я предложу другого.', reply_markup=m.dialog_markup)
    else:
        text = await sync_to_async(get_random_form)(member)
        await cb.message.answer(text=text, reply_markup=m.form_markup)


@dp.callback_query_handler(text='repeat_form', state=[UserState, None])
async def repeate_dialog(cb: types.callback_query):
    member = await sync_to_async(Member.objects.get)(telegram_id=cb['from']['id'])
    text = await sync_to_async(get_random_form)(member)
    await cb.message.answer(text=text, reply_markup=m.form_markup)


@dp.callback_query_handler(text='dialog_logic', state=[UserState, None])
async def form_start(cb: types.callback_query):
    await cb.message.answer("Введите своё имя")
    await cb.answer()
    await UserState.name.set()


@dp.message_handler(state = UserState.name)
async def name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await UserState.age.set()


@dp.message_handler(state = UserState.age)
async def age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В какой компании работаешь?")
    await UserState.company.set()


@dp.message_handler(state = UserState.company)
async def company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("Должность?")
    await UserState.job.set()


@dp.message_handler(state = UserState.job)
async def job(message: types.Message, state: FSMContext):
    await state.update_data(job=message.text)
    await message.answer("С какими технологиями работаешь?")
    await UserState.stack.set()


@dp.message_handler(state=UserState.stack)
async def stack(message: types.Message, state: FSMContext):
    await state.update_data(stack=message.text)
    await message.answer("Какое у тебя хобби?")
    await UserState.hobby.set()


@dp.message_handler(state=UserState.hobby)
async def hobby(message: types.Message, state: FSMContext):
    await state.update_data(hobby=message.text)
    await message.answer("Цель знакомства?")
    await UserState.goal.set()


@dp.message_handler(state=UserState.goal)
async def goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer("Местро проживания?")
    await UserState.region.set()


@dp.message_handler(state=UserState.region)
async def region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    payloads = await state.get_data()
    name = payloads['name']
    age = payloads['age']
    company = payloads['company']
    job = payloads['job']
    stack = payloads['stack']
    hobby = payloads['hobby']
    goal = payloads['goal']
    region = payloads['region']

    member = await sync_to_async(Member.objects.get)(telegram_id=message.from_id)

    await sync_to_async(Form.objects.create)(
          member=member,
          name=name,
          age=age,
          company=company,
          job=job,
          stack=stack,
          hobby=hobby,
          goal=goal,
          region=region)

    text = await sync_to_async(get_random_form)(member)
    await bot.send_message(message.chat.id, text=text, reply_markup=m.form_markup)


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
