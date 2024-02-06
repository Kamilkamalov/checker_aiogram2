from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_users = KeyboardButton('💼Список кошельков')
button_ADD = KeyboardButton('📌Добавить кошелек')
button_CHECK = KeyboardButton('💰Начать чек кошелька')


replykb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_users, button_ADD, button_CHECK) # добавляю кнопки в меню

# РЕШЕНИЕ С ПАГИНАЦИЕЙ
def genmarkup(data): # передаём в функцию data 
    global i
    markup = InlineKeyboardMarkup() # создаём клавиатуру
    markup.row_width = 3 # кол-во кнопок в строке
    count_for = 0
    
    for i in data: # цикл для создания кнопок
        # Если каллбек дата i[0], то отображаются все записи
        markup.add(InlineKeyboardButton(i[1], callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата.
        count_for = count_for + 1 # счетчик проходов по циклу for
        if count_for == 10: # отличное решение, контролирует 10 кошельков на одной странице пагинации
            break # выдает только 10 кошелек


    markup.add(InlineKeyboardButton('➡️ДАЛЕЕ➡️', callback_data='NEXT_LIST')) # создаю отдельную инлайн кнопку под стрелочку ДАЛЕЕ
    markup.add(InlineKeyboardButton('⬅️НАЗАД⬅️', callback_data='BACK_LIST')) # создаю отдельную инлайн кнопку под стрелочку ДАЛЕЕ
    markup.add(InlineKeyboardButton('🔄ВЕРНУТЬСЯ К 1 СТРАНИЦЕ🔄', callback_data='FIRST_LIST'))
    return markup #возвращаем клавиатуру

# УДАЛЕНИЕ КОШЕЛЬКА
def delete_wallet():
    markup_delete = InlineKeyboardMarkup() # создаём клавиатуру
    markup_delete.row_width = 3 # кол-во кнопок в строке
    markup_delete.add(InlineKeyboardButton('✅Подтверждаю', callback_data='DELETE_WALLET'))
    return markup_delete

