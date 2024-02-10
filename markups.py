import telebot

months_days = {'january': 31, 'february': 29, 'march': 31,
                'april': 30, 'may': 31, 'june': 30, 'july': 31,
                'autumn': 31, 'september': 30, 'october': 31,
                'november': 30, 'december': 31}

def get_months_markups():
    week_days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    start_day = week_days[0]
    for month, days in months_days.items():
        days_list = []
        for day in range(1, days + 1):
            if start_day == 'пн':
                days_list.append([telebot.types.InlineKeyboardButton('day', callback_data= f'{month} {day}')])
            else:
                days_list[-1].append(telebot.types.InlineKeyboardButton('day', callback_data= f'{month} {day}'))



