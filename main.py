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
    bot.send_message(call.message.chat.id, "когда вы хотите пойти?", reply_markup= eventtype_markup)

@bot.callback_query_handler(lambda call: 'months' == call.data)
def choose_months(call):
    months_lists = [[], [], [], []]
    number = 0
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data='start')
    for month, days in months_days.items():
        months_lists[number // 3].append(telebot.types.InlineKeyboardButton(month, callback_data= month))
        number += 1
    months_markup = telebot.types.InlineKeyboardMarkup(months_lists)
    months_markup.add(back_button)
    bot.send_message(call.message.chat.id, 'Выберите месяц', reply_markup= months_markup)

@bot.callback_query_handler(lambda call: call.data in months_days)
def choose_day(call):
    days_lists = [[], [], [], [], [], []]
    number = 0
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data= 'months')
    for day in range(1, months_days[call.data] + 1):
        days_lists[number // 6].append(telebot.types.InlineKeyboardButton(day, callback_data= f'{call.data} {day}'))
        number += 1
    days_markup = telebot.types.InlineKeyboardMarkup(days_lists)
    days_markup.add(back_button)
    bot.send_message(call.message.chat.id, "Выберите день: ", reply_markup= days_markup)

@bot.callback_query_handler(lambda call: len(call.data.split()) == 2)
def show_events(call):
    month_name, day_number = call.data.split()
    if month_name != 0 and day_number != 0:
        res = requests.get(f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    else:
        res = requests.get(f'https://afisha.yandex.ru/{currant_city}?date=2024-02-01&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    while "афиша" not in soup.text.lower():
        res = requests.get(f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
        soup = bs4.BeautifulSoup(res.text, 'lxml')
    all_div = soup.find_all('div', class_= 'event')
    print(soup.text)
    print(f'https://afisha.yandex.ru/{currant_city}?date=2024-{months_numbers[month_name]}-{day_number}&period=1')
    eventsname_markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton('Назад', callback_data=month_name)
    for tag in all_div:
        h2 = tag.find_next('h2').text
        a = tag.find_next('a').get('href')
        eventsname_markup.add(telebot.types.InlineKeyboardButton(h2, url= f'https://afisha.yandex.ru{a}'))
    eventsname_markup.add(back_button)
    bot.send_message(call.message.chat.id, 'Мероприятия на выбранный день:', reply_markup= eventsname_markup)

    """print(*all_div, sep= '\n')"""
    #нет соединения ;(

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(15)
