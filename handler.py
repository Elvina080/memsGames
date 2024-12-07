import os
from datetime import datetime, timedelta
from random import choice, randint
import re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from aiogram.types import Message, CallbackQuery, InputFile, BufferedInputFile, \
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, \
    LabeledPrice, PreCheckoutQuery, ReplyKeyboardMarkup, KeyboardButton

from messages import MessageText
from aiogram.fsm.context import FSMContext


load_dotenv()  # загружает переменные из файла .env в переменные окружения
router = Router()
CHAT_ID = os.getenv('CHAT_ID')



print('start')

# ITEMS

photo_types = {
    'jpg': list(range(1, 6)) + list(range(7, 17)) + list(range(18, 22)) + list(
    range(24, 35)) + list(range(39, 42)),
    'png': [6, 17, 37],
    'jpeg': [22, 23, 35, 36, 38] + list(range(42, 51))
}



class Teams(StatesGroup):
    # teams = [
    #     (team1, points1),
    #     (team2, points2)
    # ]
    teams = State()
    # round = {
    #     'team_id': id
    #     'time_start': datatime,
    #     'time_end': datatime,
    #     'ok': points,
    #     'not_ok': points
    # }
    round = State()
    # mode = 0 / - 1
    mode = State()
    round_cnt = State()  # Счетчик раундов


RANDOM_TEAM_NAMES = [
    "🏆 Мемные Легенды",
    "😬 Школа кринжа",
    "🤣 Легенды рофлов",
    "🎵 Пантеон Баянчиков",
    "🤖 Кекатели 3000",
    "😂 Фабрика лулзов",
    "🦖 Мемозавры",
    "😐 Почти смешно",
    "🔥 Кринжевики",
    "⚔️ Герои Баяна",
    "🌈 Дети Лололенда"
]



# KEYBOARDS
def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🎮 Новая игра')],
            [KeyboardButton(text='📜 Правила')],
            [KeyboardButton(text='💰 Поддержать')],
            [KeyboardButton(text='❓ Помощь')],
        ],
        resize_keyboard=True,
    )

def get_mode() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🤯 Вычитать 1 балл при пропуске', callback_data=f'mode_1')],
        [InlineKeyboardButton(text='🥱 НЕ вычитать баллы при пропуске', callback_data=f'mode_2')],
    ])

def get_teams_markup(first = False) -> InlineKeyboardMarkup:
    teams_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎲 Рандомное название', callback_data='random_team')],
        [InlineKeyboardButton(text='🛑 Больше нет команд', callback_data='finish_teams')],
    ])
    if first:
        teams_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🎲 Рандомное название',
                                  callback_data='random_team')],
        ])
    return teams_markup

def get_start(team_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚀 Старт', callback_data=f'play_{team_id}')],
    ])

def get_select_res() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Угадали', callback_data=f'res_ok')],
        [InlineKeyboardButton(text='❌ Пропустили', callback_data=f'res_notok')],
    ])

def get_select_res_end() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Угадали', callback_data='res-end_ok')],
        [InlineKeyboardButton(text='❌ Пропустили', callback_data='res-end_notok')],
    ])

def get_teams_list(teams) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text=teams[i][0],
                                      callback_data=f'team_{i}')] for i in
                range(len(teams))]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_continue() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎉 Играем дальше', callback_data='continue_1')],
        [InlineKeyboardButton(text='🏁 Закончить игру', callback_data='continue_0')],
    ])


donation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🌥️ Cloudtips',
                          url='https://pay.cloudtips.ru/p/d1db20d4')],
])


# HELPERS
async def get_rules(message: Message=None, callback: CallbackQuery=None):
    if message:
        await message.answer(MessageText.mems_rules)
    else:
        await callback.message.answer(MessageText.mems_rules)

def mode_filter(callback: CallbackQuery):
    pattern = r"^mode_\d+$"
    return re.match(pattern, callback.data) is not None


def get_names_list(teams: list):
    return [item[0] for item in teams]


def get_photo_type(img_id):
    for key, values in photo_types.items():
        if img_id in values:
            return key

def get_random_photo():
    img_id = randint(1, 50)
    img_type = get_photo_type(img_id)
    return f'https://storage.yandexcloud.net/memsgames/{img_id}.{img_type}'

def team_filter(callback: CallbackQuery):
    pattern = r"^team_\d+$"
    return re.match(pattern, callback.data) is not None


def play_filter(callback: CallbackQuery):
    pattern = r"^play_\d+$"
    return re.match(pattern, callback.data) is not None

def res_filter(callback: CallbackQuery):
    key = 'res'
    return key == callback.data.split('_')[0]

def res_end_filter(callback: CallbackQuery):
    key = 'res-end'
    return key == callback.data.split('_')[0]

def continue_filter(callback: CallbackQuery):
    pattern = r"^continue_\d+$"
    return re.match(pattern, callback.data) is not None








# ROUTER
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.bot.send_message(CHAT_ID, f'NewUser: @{message.from_user.username}')
    await message.answer(MessageText.start_memalias, reply_markup=get_main_keyboard())
    await get_rules(message=message)

@router.message(F.text == '📜 Правила')
async def rules(message: Message):
    await get_rules(message=message)

@router.message(F.text == '💰 Поддержать')
async def rules(message: Message):
    await message.answer(MessageText.donation, reply_markup=donation)

@router.message(F.text == '❓ Помощь')
async def rules(message: Message):
    await message.answer(MessageText.help)

@router.message(F.text == '🎮 Новая игра')
async def new_game(message: Message, state: FSMContext):
    """Начало новой игры и инициализация команд."""
    await state.clear()
    await state.update_data(round_cnt=0)
    await message.answer(MessageText.start_game)
    await message.answer(MessageText.select_mode, reply_markup=get_mode())



@router.callback_query(mode_filter)
async def state_mode(callback: CallbackQuery, state: FSMContext):
    mode = callback.data.split('_')[1]
    await state.update_data(mode=- 1 if mode == '1' else 0)
    await callback.message.answer(MessageText.mode_1 if mode == '1' else MessageText.mode_2)
    await callback.message.answer(MessageText.create_teams, reply_markup=get_teams_markup(first=True))
    await state.set_state(Teams.teams)

@router.message(Teams.teams)
async def new_team(message: Message, state: FSMContext):
    team_name = message.text.strip()
    data = await state.get_data()
    teams = data.get("teams", [])
    if team_name in get_names_list(teams):
        await message.answer(text=MessageText.team_already_exist(team_name))
        return
    # Добавляем новую команду с баллом 0
    teams.append([team_name, 0])
    await state.update_data(teams=teams)
    # Просим ввести следующую команду или завершить
    await message.answer(
        MessageText.team_added(team_name),
        reply_markup=get_teams_markup()
    )

@router.callback_query(F.data == 'random_team')
async def random_team(callback: CallbackQuery, state: FSMContext):
    """Генерация случайного названия команды."""
    data = await state.get_data()
    teams = data.get("teams", [])

    # Выбираем случайное название, которое не повторяется
    available_names = [name for name in RANDOM_TEAM_NAMES if name not in get_names_list(teams)]
    if not available_names:
        await callback.message.answer("Больше нет доступных названий для команд.")
        return

    random_name = choice(available_names)
    teams.append([random_name, 0])
    await state.update_data(teams=teams)

    await callback.message.answer(
        MessageText.team_added(random_name),
        reply_markup=get_teams_markup()
    )

@router.callback_query(F.data == "finish_teams")
async def finish_collecting_teams(callback: CallbackQuery, state: FSMContext):
    # Получаем команды из состояния
    data = await state.get_data()
    teams = data.get("teams", [])
    # Выводим список команд
    if teams:
        await callback.message.answer(MessageText.teams_end, reply_markup=get_teams_list(teams))
    else:
        await callback.message.answer("Не добавлено ни одной команды. Попробуй снова!")




@router.callback_query(team_filter)
async def play_team(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    teams = data.get("teams", [])
    team_id = int(callback.data.split('_')[1])
    round_cnt = data.get("round_cnt", 0) + 1
    await state.update_data(round_cnt=round_cnt)
    team_name = get_names_list(teams)[team_id]
    await callback.message.answer(MessageText.selected_team(team_name, round_cnt),
                                    reply_markup=get_start(team_id))





@router.callback_query(play_filter)
async def play_team(callback: CallbackQuery, state: FSMContext):
    team_id = int(callback.data.split('_')[1])
    current_time = datetime.now()
    time_plus_thirty_seconds = current_time + timedelta(seconds=30)
    time_plus_one_minute = current_time + timedelta(minutes=1)
    team_round = {
        'team_id': int(team_id),
        'time_start': current_time,
        'time_middle': time_plus_thirty_seconds,
        'time_end': time_plus_one_minute,
        'ok': 0,
        'not_ok': 0
    }
    await state.update_data(round=team_round)
    user_id = callback.from_user.id
    photo = get_random_photo()
    await callback.message.bot.send_photo(
        chat_id=user_id,
        photo=photo,
        # caption=str,
        reply_markup=get_select_res()
    )


@router.callback_query(res_filter)
async def play_forward(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_round = data.get('round', dict())
    current_time = datetime.now()
    time_middle = team_round.get('time_middle')
    time_end = team_round.get('time_end')
    markup = get_select_res()
    res = callback.data.split('_')[1]
    if res == 'ok':
        team_round['ok'] = team_round['ok'] + 1
    else:
        team_round['not_ok'] = team_round['not_ok'] + 1
    await state.update_data(round=team_round)

    if time_end > current_time > time_middle:
        await callback.message.answer(MessageText.left_time)

    if current_time > time_end:
        await callback.message.answer(MessageText.time_end)
        markup = get_select_res_end()

    user_id = callback.from_user.id
    photo = get_random_photo()
    await callback.message.bot.send_photo(
        chat_id=user_id,
        photo=photo,
        reply_markup=markup
    )

@router.callback_query(res_end_filter)
async def play_round_end(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_round = data.get('round', dict())
    team_id = team_round.get('team_id')
    round_cnt = data.get('round_cnt', 0)
    teams = data.get('teams')
    res = callback.data.split('_')[1]
    if res == 'ok':
        team_round['ok'] = team_round['ok'] + 1
    else:
        team_round['not_ok'] = team_round['not_ok'] + 1
    round_ok = team_round.get('ok')
    round_not_ok = team_round.get('not_ok')
    await callback.message.answer(MessageText.round_result(ok=round_ok, not_ok=round_not_ok))

    new_points = round_ok + (round_not_ok * data.get('mode'))
    teams[team_id][1] = teams[team_id][1] + new_points
    await state.update_data(teams=teams)

    await callback.message.answer(MessageText.all_results(teams, round_cnt), reply_markup=get_continue())

@router.callback_query(continue_filter)
async def continue_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    teams = data.get('teams')
    status = callback.data.split('_')[1]
    if int(status):
        await callback.message.answer(MessageText.select_next_team, reply_markup=get_teams_list(teams))
    else:
        winner = max(teams, key=lambda team: team[1])
        await callback.message.answer(MessageText.end_game(winner[0]), reply_markup=get_main_keyboard())
        await state.clear()


