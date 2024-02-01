import telebot
import bs4
import requests
from time import sleep

bot = telebot.TeleBot('6578966055:AAGysIe59xeV7J91bMhf5dwvv30Q0VRM2uw')
cities_dict = {'Москва': 'moscow', 'Казань': 'kazan', 'Новосибирск': 'novosibirsk'}
currant_city = 'moscow'
months_days = {'january': 31, 'february': 28, 'march': 31,
                'april': 30, 'may': 31, 'june': 30, 'july': 31,
                'autumn': 31, 'september': 30, 'october': 31,
                'november': 30, 'december': 31}

months_numbers = {'january': '01', 'february': '02', 'march': '03',
                'april': '04', 'may': '05', 'june': '06', 'july': '07',
                'autumn': '08', 'september': '09', 'october': '10',
                'november': '11', 'december': '12'}

def get_months_markup(call):
    months_lists = [[], [], [], []]
    number = 0
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data='start')
    for month, days in months_days.items():
        months_lists[number // 3].append(telebot.types.InlineKeyboardButton(month, callback_data=f'{month}|{call.data}'))
        number += 1
    months_markup = telebot.types.InlineKeyboardMarkup(months_lists)
    months_markup.add(back_button)
    return months_markup

def get_days_markup(month):
    days_lists = [[], [], [], [], [], []]
    number = 0
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data='months')
    for day in range(1, months_days[month] + 1):
        days_lists[number // 6].append(telebot.types.InlineKeyboardButton(day, callback_data=f'{month} {day}'))
        number += 1
    days_markup = telebot.types.InlineKeyboardMarkup(days_lists)
    days_markup.add(back_button)
    return days_markup

def get_eventsname_markup(call):
    month_name, day_number = call.data.split()
    if month_name != 0 and day_number != 0:
        res = requests.get(
            f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    else:
        res = requests.get(f'https://afisha.yandex.ru/{currant_city}?date=2024-20-02&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    while "афиша" not in soup.text.lower():
        res = requests.get(
            f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    all_div = soup.find_all('div', class_='event')
    print(soup.text)
    print(f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
    eventsname_markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data=month_name)
    for tag in all_div:
        h2 = tag.find_next('h2').text
        a = tag.find_next('a').get('href')
        eventsname_markup.add(telebot.types.InlineKeyboardButton(h2, url=f'https://afisha.yandex.ru{a}'))
    eventsname_markup.add(back_button)
    return eventsname_markup
@bot.message_handler(commands= ['start'])
def start(mes : telebot.types.Message):
    cities_markup = telebot.types.InlineKeyboardMarkup()
    for city, eng_city in cities_dict.items():
        cities_markup.add(telebot.types.InlineKeyboardButton(city, callback_data= eng_city))
    bot.send_message(mes.chat.id, f'Привет, {mes.from_user.username}!')
    bot.send_message(mes.chat.id, 'Выберите город: ', reply_markup= cities_markup)

@bot.callback_query_handler(lambda call : call.data == 'start')
def back_to_start(call):
    cities_markup = telebot.types.InlineKeyboardMarkup()
    for city, eng_city in cities_dict.items():
        cities_markup.add(telebot.types.InlineKeyboardButton(city, callback_data= eng_city))
    bot.send_message(call.message.chat.id, f'Привет, {call.message.from_user.username}!')
    bot.send_message(call.message.chat.id, 'Выберите город: ', reply_markup= cities_markup)

@bot.callback_query_handler(lambda call: call.data in cities_dict.values())
def choose_type(call):
    global currant_city
    currant_city = call.data
    eventtype_markup = telebot.types.InlineKeyboardMarkup(row_width= 1)
    data_button = telebot.types.InlineKeyboardButton('выбрать дату', callback_data= 'months')
    period_button = telebot.types.InlineKeyboardButton('выбрать период', callback_data= 'months period')
    immdate_button = telebot.types.InlineKeyboardButton('показать ближайшие мероприятия', callback_data= 'near')
    eventtype_markup.add(data_button, period_button, immdate_button)
    bot.send_message(call.message.chat.id, f"когда вы хотите пойти на мероприятие в {currant_city}?", reply_markup= eventtype_markup)

@bot.callback_query_handler(lambda call: 'months' in call.data)
def choose_months(call : telebot.types.CallbackQuery):
    #bot.send_message(call.message.chat.id, f'Выберите месяц для выбора даты в городе {currant_city}', reply_markup= months_markup)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, call.inline_message_id, reply_markup= get_months_markup(call))

@bot.callback_query_handler(lambda call: call.data.split('|')[0] in months_days)
def choose_day(call):
    month, chose_type = call.data.split('|')
    # bot.send_message(call.message.chat.id, f"Выберите день на {call.data} города {currant_city}", reply_markup= days_markup)
    if chose_type == 'months':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, call.inline_message_id, reply_markup= get_days_markup(month))


@bot.callback_query_handler(lambda call: len(call.data.split()) == 2)
def show_events(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, call.inline_message_id, reply_markup= get_eventsname_markup(call))
    #bot.send_message(call.message.chat.id, f'Мероприятия на {day_number}-ое {month_name} города {currant_city}', reply_markup=eventsname_markup)
    """print(*all_div, sep= '\n')"""
    #нет соединения ;(

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(15)
