from os import link
from pickle import NONE
from tkinter.tix import TEXT
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiohttp import Payload
import keyboards as nav

from keyboards import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import logging
import sqlite3
import asyncio # асинхронка для поздних логов

from config import TOKEN

# рефералка
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram import types

# счетчик
from collections import Counter

from config import TOKEN, CHANNEL_OUTPUT

from aiogram.dispatcher import FSMContext # машина состояний
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
   
# from checkGPT import CHECKGPT
import json

# дата
from datetime import datetime
# фильтры
from aiogram.dispatcher import filters
# ЧЕК
from GPTchecker import *

# Пишу для логирования в терминале, чтобы понять где мои ошибки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

CHANNEL_ID = '-1001772153224' # айди канала для всех логов СМЕНИТЬ КАНАЛ!

#base = sqlite3.connect('data.db') # создание подключения
#cur = conn.cursor('') # cur для взаимодействия с бд
#cur.execute('CREATE TABLE users(user_id INTEGER, username TEXT)') # добавил строку
def sql_start():
    global base, cur
    base = sqlite3.connect('data.db')
    cur = base.cursor()
    if base:
        print('База данных существует или успешно создана')
    else:
        print('Базы нету')
    base.execute('CREATE TABLE IF NOT EXISTS data(wallets, accs, notes, balance, transactions, adder, date, RowNumber)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id, count_rows_page)')
    base.commit()
sql_start() # запускаем функцию с БД



# добавляю юзера в бд при /start НО ТУТ ПРОСТО ПРИВЕТСТВИЕ
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('{user}'.format(user=message.from_user.full_name) + ", welcome!", reply_markup = nav.replykb)
    cur.execute('INSERT INTO "users" (user_id, count_rows_page) VALUES ("{message.from_user.id}", "0")') # добавляю юзера в пагинацию
    base.commit()


# Вывожу список кошельков ✅
@dp.message_handler(content_types=['text'], text='💼Список кошельков', state="*") # state='*' в хэндлер из ответов НЕ ВОРК
async def buy(message: types.Message):
    if (message.from_user.id == 1277630121 or message.from_user.id == 5980476622): # ВЫ В БЕЛОМ СПИСКЕ?
        print(message.from_user.id)
        cur.execute('SELECT * FROM data')
        data = cur.fetchall()
        await bot.send_message(message.from_user.id, '💼Список кошельков:', reply_markup=nav.genmarkup(data))
        base.commit()
    else:
        await bot.send_message(message.from_user.id, 'Вы не в белом списке')
        

# Перелистываю страницу в пагинации вправо  ✅
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'NEXT_LIST')
async def process_callback_NEXT_LIST(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == 'NEXT_LIST':
        cur.execute('SELECT count_rows_page FROM "users" WHERE user_id LIKE ?', (callback_query.from_user.id,)) # 1 ступень - извлекаю значение страницы
        count_rows, = cur.fetchone()
        print(count_rows) # число без кавычек, скобок и запятых
        count_rows = count_rows + 10 # прибавляю 10 чтобы ориентироваться в пагинации конкретного юзера
        base.commit()
        cur.execute('UPDATE users SET count_rows_page = ? WHERE user_id LIKE ?', (count_rows, callback_query.from_user.id)) # обновляю запись пагинации
        base.commit()
        cur.execute('SELECT * FROM data LIMIT 10 OFFSET ?', (count_rows, )) # игнорирую - OFFSET первые 10 и считываю - LIMIT следующие 10 строк
        data10 = cur.fetchall()
        await bot.send_message(callback_query.from_user.id, '💼Список кошельков:', reply_markup=nav.genmarkup(data10))
        base.commit()

# Перелистываю страницу в пагинации назад  ✅
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'BACK_LIST')
async def process_callback_BACK_LIST(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == 'BACK_LIST':
        cur.execute('SELECT count_rows_page FROM "users" WHERE user_id LIKE ?', (callback_query.from_user.id,)) # 1 ступень - извлекаю значение страницы
        count_rows, = cur.fetchone()
        print(count_rows) # число без кавычек, скобок и запятых
        count_rows = count_rows - 10 # отнимаю 10 чтобы ориентироваться в пагинации конкретного юзера
        if count_rows < 0:
            count_rows = 0
        print(count_rows)
        base.commit()
        cur.execute('UPDATE users SET count_rows_page = ? WHERE user_id LIKE ?', (count_rows, callback_query.from_user.id)) # обновляю запись пагинации
        base.commit()
        cur.execute('SELECT * FROM data LIMIT 10 OFFSET ?', (count_rows, )) # игнорирую - OFFSET первые 10 и считываю - LIMIT следующие 10 строк
    data10 = cur.fetchall()
    await bot.send_message(callback_query.from_user.id, '💼Список кошельков:', reply_markup=nav.genmarkup(data10))
    base.commit()
    
# Возвращаюсь на первую страницу ✅
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'FIRST_LIST')
async def process_callback_FIRST_LIST(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Вернулся на первую страницу')
    count_rows = 0
    print(count_rows)
    cur.execute('UPDATE users SET count_rows_page = ? WHERE user_id LIKE ?', (count_rows, callback_query.from_user.id)) # обновляю запись пагинации
    base.commit()
    cur.execute('SELECT * FROM data LIMIT 10 OFFSET ?', (count_rows, )) # игнорирую - OFFSET первые 10 и считываю - LIMIT следующие 10 строк
    data1 = cur.fetchall()
    await bot.send_message(callback_query.from_user.id, '💼Список кошельков:', reply_markup=nav.genmarkup(data1))
    base.commit()

# FSM !!!
class FSMGO(StatesGroup):
    wallet = State()
    accs = State()
    notes = State()
# команда
@dp.message_handler(commands=['new'])
async def cmd_new(message: types.Message) -> None:
    await message.reply("Начинаем добавление кошелька:\n💳Введите кошелек")
    await FSMGO.wallet.set() # установили состояние кошелька????


@dp.message_handler(state=FSMGO.wallet)
async def load_wallet(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['wallet'] = message.text
    await message.reply('Теперь введите данные аккаунта🔗')
    await FSMGO.next()

@dp.message_handler(state=FSMGO.accs)
async def load_accs(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['acc'] = message.text
    await message.reply('Укажите примечание🔗\nНе оставляйте поле пустым, вдруг потом пригодится!')
    await FSMGO.next()

@dp.message_handler(state=FSMGO.notes)
async def check_notes(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['notes'] = message.text
        await message.reply(f"{data['wallet']}\n{data['acc']}\n{data['notes']}")
    await message.reply('Кошелек добавлен в базу📌')
    await state.finish()


    # получаю кол-во строк
    cur.execute('SELECT COUNT(*) FROM data') # получаю номер строки
    Rows_count = cur.fetchone()
    Row_Number = Rows_count[0] + 1 # получаю первый элемент кортежа и складываю его с 1, чтобы получить номер новой сейча создаваемой строки
    base.commit()


    base.execute("INSERT INTO data (wallets, accs, notes, adder, date) VALUES (?, ?, ?, ?, ?)", (data['wallet'], data['acc'], data['notes'], message.from_user.full_name, datetime.now()))
    base.commit()


# ФИЛЬТР НА КАЛБЭК ХАХАХА
@dp.callback_query_handler(filters.Text(equals='DELETE_WALLET')) 
async def process_callback_DELETE_WALLET(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id) # чтобы кнопка не переливалась, типа ответил на коллбэк
    await bot.send_message(callback_query.from_user.id, f'Чтобы подтвердить действие введите слово "удалить" без кавычек\n'
        f'И кошелек без пробела\nПример: удалитьbc123343567ygergg'
    f'\nВНИМАНИЕ! Если ввести другой существующий кошелек, то удалится он!\n🚬🗿') # теперь я передаю в функцию ниже
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    
# # УДАЛЕНИЕ ИЗ БАЗЫ ПОСЛЕ ФИЛЬТРА
@dp.message_handler(filters.Text(contains='удалить'))
async def bot_message(message: types.Message):
    #global confirmation
    confirmation = message.text
    confirmation = confirmation.replace('удалить', '')
    cur.execute('DELETE FROM data WHERE wallets = (?)', (confirmation, )) # удаляю в соответствии с выбранным кошельком
    await message.reply(text='Успешное удаление')




# Добавляю кошелек
@dp.message_handler(filters.Text(equals='📌Добавить кошелек')) #content_types=['text'], text='📌Добавить кошелек', 
async def add_wallet(message: types.Message):
    if (message.from_user.id == 1277630121 or message.from_user.id == 5980476622):
        await cmd_new(message)
    else:
        await bot.send_message(message.from_user.id, 'Вы не в белом списке')

# Ставлю кошелек на проверку
@dp.message_handler(filters.Text(equals='💰Начать чек кошелька'))
async def check_wallet(message: types.Message):
    if (message.from_user.id == 1277630121 or message.from_user.id == 5980476622):
        await bot.send_message(message.from_user.id, 'Кошелек будет поставлен на проверку.\n'
            f'Информация о новых транзакциях будет обновляться каждые 30 секунд.\n'
            f'Введите интересуемый кошелек со словом в начале: чек\n'
            f'Пример: чекbc1qvhxafz8dqk8c25jsx669yd6qrxhl5dx72dyryp')
    else:
        await bot.send_message(message.from_user.id, 'Вы не в белом списке')

# РЕАЛЬНО СТАВЛЮ НА ПРОВЕРКУ
@dp.message_handler(filters.Text(contains='чек'))
async def bot_message(message: types.Message):
    confirmation_check = message.text
    confirmation_check = confirmation_check.replace('чек', '')
    await message.reply(text='Кошелек поставлен на чек. Я сообщу, если будет пополнение♻️')
    await check_new_transaction(confirmation_check)
    if NEW_TRANSACTION == '💸Новая транзакция!💸':
        await bot.send_message(message.from_user.id, '💸Новая транзакция!💸')
    
# # ОСТАНОВИТЬ ЧЕКЕР ФУЛЛ
# @dp.message_handler(filters.Text(contains='прекратить'))
# async def bot_message(message: types.Message):


# тут чисто инфу вынимаю из бд для цикла кнопок в keyboards.py
@dp.callback_query_handler(lambda call: True)
async def stoptopupcall(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id) # ответ на колбэк, чтобы кнопка не ожидала
    cur.execute('SELECT * FROM data') #получаем наши идентификаторы
    sqldata = cur.fetchall() # в список их
    sortdata = [] # список отсортированных
    for i in sqldata: # сортируем
        sortdata.append(i[0]) # добавляем отсортированные tgid в список
    if callback_query.data in sortdata: # делаем проверку есть ли наш идентификатор в тех кнопках
        cur.execute('SELECT * FROM data WHERE wallets = (?)', (callback_query.data, )) # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
        userinfo = cur.fetchall() # в список добавляем.
        await bot.send_message(callback_query.from_user.id, f'<b>Кошелек:</b> <code>{userinfo[0][0]}</code>'
                               f'\n<b>Аккаунт:</b> <code>{userinfo[0][1]}</code>'
                               f'\n<b>Заметки(площадка и прочее):</b> <code>{userinfo[0][2]}</code>'
                               f'\n<b>Баланс:</b> <code>{userinfo[0][3]}</code>'
                               f'\n<b>Транзакции:</b> <code>{userinfo[0][4]}</code>'
                               f'\n<b>Добавил:</b> <code>{userinfo[0][5]}</code>'
                               f'\n<b>Дата добавления в базу:</b> <code>{userinfo[0][6]}</code>', parse_mode='HTML') # делаем вывод инфы
        await bot.send_message(callback_query.from_user.id, 'Удалить этот кошелек?', reply_markup=nav.delete_wallet())
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


#  поллинг = опрашиваю сервера телеграм о новых сообщениях?
if __name__ == '__main__':
    executor.start_polling(dp)
        