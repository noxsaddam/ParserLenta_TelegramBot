from pprint import pprint
import config
import telebot
from telebot import types
import parser_lenta
import json
from urllib.request import urlopen
bot = telebot.TeleBot(config.token)
print("Bot - works")


class Get_viski:
    __instance = None
    __id_users = None

    def __new__(cls, *args, **kwargs):
        cls.__instance = super().__new__(cls) if cls.__instance is None else cls.__instance
        return cls.__instance

    def __init__(self, id_users, refresh=False):
        self.t = 1
        if not hasattr(self, 'viski_list') or self.__class__.__id_users != id_users or refresh is True:
            print("Создаю итератор")
            self.viski_list = iter(parser_lenta.get_data())
            self.__class__.__id_users = id_users

    def __iter__(self):
        for i in self.viski_list:
            yield i

    def __next__(self):
        try:
            return next(self.viski_list)
        except StopIteration as er:
            raise er


def get_button_viski():
    # Создание кнопки
    markup = types.InlineKeyboardMarkup()
    button_viski = types.InlineKeyboardButton("Viski", callback_data="Viski")
    markup.add(button_viski)
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    print('Start - OK')
    # Keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/Viski_Discount")
    item2 = types.KeyboardButton("/start")
    markup.add(item1, item2)
    mess = f"Добро пожаловать <b>{message.from_user.first_name}</b>!"
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=["Viski_Discount"])
def viski_discount(message):
    bot.send_message(message.chat.id, "Я подготовлю список виски со скидкой, подождите")
    viski_iter = Get_viski(message.chat.id, refresh=True)
    bot.send_message(message.chat.id, "Все готово, я подготовил 48 позиций, нажмите кнопку 'Viski' для отоброжения товара",
                     reply_markup=get_button_viski())


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    viski_iter = Get_viski(callback.message.chat.id)
    if callback.data == "Viski":
        try:
            viski = next(viski_iter)
            count_picture = viski['count_picture']
            picture = open(f'img/img_{count_picture}.png', 'rb')
            mess = f'Описание: {viski["title"]}\nЦена со скидкой: {viski["price_sale"]}\nЦена без скидки: ' \
                   f'{viski["price_full"]}\nРазмер скидки: {viski["discount"]}\nСсылка на товар: {viski["href"]}'
            print(mess)
            print()
            print(count_picture)
            bot.send_photo(callback.message.chat.id, picture)
            bot.send_message(callback.message.chat.id, mess, reply_markup=get_button_viski())
        except StopIteration:
            bot.send_message(callback.message.chat.id, "Я предложил 48 самых интересных позиций, на этом мои полномочия...")


bot.polling(none_stop=True)
