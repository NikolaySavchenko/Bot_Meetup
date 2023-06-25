import asyncio
import logging
import os
import random
from pathlib import Path

from django.utils import timezone

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
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


from meetup_bot.models import Member, Presentation, Form, Donation

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
    question = State()
    anounce = State()
    donate = State()


@dp.message_handler()
async def start_conversation(msg: types.Message, state: FSMContext):
    if msg['from']['username']:
        member, created = await sync_to_async(Member.objects.get_or_create)(telegram_id=msg.from_id, telegram_name=msg['from']['username'])
    else:
        member, created = await sync_to_async(Member.objects.get_or_create)(telegram_id=msg.from_id)
    message = f'Приветствую, {member.telegram_name}'
    await msg.answer(message)
    await msg.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text='about_bot')
async def about_bot(cb: types.callback_query):
    message = 'Данный бот позволяет получить информацию о расписании митапа и задать вопросы текущему спикеру'
    await cb.message.answer(message)
    await cb.message.answer('Main menu', reply_markup=m.client_start_markup)


@dp.callback_query_handler(text='participate_in_meetup', state=[UserState, None])
async def participate(cb: types.callback_query, state: FSMContext):
    await state.reset_state(with_data=False)
    member = await sync_to_async(Member.objects.get)(telegram_id=cb['from']['id'])
    if member.role == 'organizer':
        await cb.message.answer('Organizer menu', reply_markup=m.organizer_markup)
    else:
        await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='anounce')
async def ask_anounce(cb: types.callback_query):
    await cb.message.delete()
    await cb.message.answer('Введите текст оповещения')
    await UserState.anounce.set()
    await cb.answer()


@dp.message_handler(lambda msg: msg.text, state=UserState.anounce)
async def anounce(msg: types.Message, state: FSMContext):
    members = await sync_to_async(Member.objects.exclude)(telegram_id=msg.from_id)
    async for member in members:
        await bot.send_message(member.telegram_id, msg.text)
    await msg.answer('Organizer menu', reply_markup=m.organizer_markup)


@dp.callback_query_handler(text='next_presentation', state=[UserState, None])
async def next_presentation(cb: types.callback_query):
    message = 'Следующий доклад активен'

    curent_presentation = await sync_to_async(Presentation.objects.get)(is_active_now=True)
    delay = (timezone.localtime(timezone.now()) -
             (curent_presentation.start_time +
              curent_presentation.duration))
    cpd = await sync_to_async(curent_presentation.start_time.date)()
    today_presentations = await sync_to_async(Presentation.objects.filter)(start_time__date=cpd)
    future_presentations = await sync_to_async(lambda: today_presentations.filter(start_time__gt=curent_presentation.start_time).order_by('start_time'))()
    async for future_presentation in future_presentations:
        future_presentation.start_time = future_presentation.start_time + delay
        await sync_to_async(future_presentation.save)()
    curent_presentation.is_active_now = False
    await sync_to_async(curent_presentation.save)()
    if future_presentations.first():
        following_presentation = await sync_to_async(future_presentations.first)()
        following_presentation.is_active_now = True
        await sync_to_async(following_presentation.save)()

    await cb.message.answer(message)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='schedule', state=[UserState, None])
async def show_schedule(cb: types.callback_query):
    messages = []
    curent_presentation = await sync_to_async(Presentation.objects.get)(is_active_now=True)
    cpd = await sync_to_async(curent_presentation.start_time.date)()
    today_presentations = await sync_to_async(Presentation.objects.filter)(start_time__date=cpd)
    future_presentations = await sync_to_async(lambda: today_presentations.filter(start_time__gte=curent_presentation.start_time).order_by('start_time'))()
    if future_presentations:
        async for future_presentation in future_presentations:
            start_time = future_presentation.start_time.strftime('%H:%M')
            info = f'{future_presentation.topic} начинается в {start_time} и продлится {future_presentation.duration}'
            await sync_to_async(messages.append)(info)
        msg = ('\n '.join(messages))
    else:
        msg = 'На сегодня доклады закончились'
    await cb.message.answer(msg)
    await cb.message.answer('Meetup menu', reply_markup=m.participate_markup)


@dp.callback_query_handler(text='ask_question')
async def ask_question(cb: types.callback_query):
    await cb.message.delete()
    await cb.message.answer('Введите ваш вопрос')
    await UserState.question.set()
    await cb.answer()


@dp.message_handler(lambda msg: msg.text, state=UserState.question)
async def question(msg: types.Message, state: FSMContext):
    curent_presentation = await sync_to_async(Presentation.objects.get)(is_active_now=True)
    member = await sync_to_async(Member.objects.get)(id=curent_presentation.member.id)
    await bot.send_message(member.telegram_id, msg.text)
    await msg.answer('Meetup menu', reply_markup=m.participate_markup)


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


@dp.message_handler(state=UserState.name)
async def name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В какой компании работаешь?")
    await UserState.company.set()


@dp.message_handler(state=UserState.company)
async def company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("Должность?")
    await UserState.job.set()


@dp.message_handler(state=UserState.job)
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
async def donation_size(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.answer('Введите сумму доната:')
    await UserState.donate.set()


@dp.message_handler(lambda msg: msg.text, state=UserState.donate)
async def make_donation(msg: types.Message, state: FSMContext):
    if not msg.text.isnumeric():
        await msg.answer('Сумма должна быть числом')
        return
    txt = 'Донат организаторам митапа'
    price = types.LabeledPrice(
        label=txt,
        amount=int(msg.text) * 100
    )
    await bot.send_invoice(
        msg.chat.id,
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


@dp.pre_checkout_query_handler(lambda query: True, state=UserState.donate)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await sync_to_async(print)('1')
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(
    content_types=ContentType.SUCCESSFUL_PAYMENT,
    state=[UserState, None]
)
async def successful_payment(message: types.Message, state: FSMContext):
    donate = message.successful_payment.total_amount // 100
    donate_time = timezone.localtime(timezone.now())
    await bot.send_message(
        message.chat.id,
        f'Спасибо за донат на сумму {donate}'
        f' {message.successful_payment.currency}'
    )
    member = await sync_to_async(Member.objects.get)(telegram_id=message.from_id)
    Donation.objects.create(member=member, donation=donate, donate_time=donate_time)
    member = await sync_to_async(Member.objects.get)(telegram_id=message.from_id)
    if member.role == 'organizer':
        await message.answer('Organizer menu', reply_markup=m.organizer_markup)
    else:
        await message.answer('Meetup menu', reply_markup=m.participate_markup)


executor.start_polling(dp, skip_updates=False)
