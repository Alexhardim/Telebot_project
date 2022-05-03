import config, sqlite3, logging, random, smtplib, time, requests
import datetime
from aiogram import Bot, Dispatcher, executor, types
from filter import IsAdminFilter
from SonoffBasic.sonoff import Sonoff
import devises
import threading
cod = False
register = False


def f(f_stop):
    # do something here ...
    if not f_stop.is_set():
        # call f() again in 60 seconds
        threading.Timer(60, f, [f_stop]).start()


# курс доллара
data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
USD = data['Valute']['USD']['Value']


# Настойка бота
# ----------------------------
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.Token)

dp = Dispatcher(bot)
dp.filters_factory.bind(IsAdminFilter)

# ---------------------------------------------
sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
device = {}
for i in sonoff.devices:
    n = i['name']
    device[n] = i['deviceid']
dev = []
print(config.r)


for i in range(len(config.result)):
    config.r.append(config.result[i][0])
print(config.r)
for i in range(len(config.result2)):
    config.gm.append(config.result2[i][0])

# стартовая функция
@dp.message_handler(commands=['start'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    global t

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(text='Курс доллара')
    button2 = types.KeyboardButton(text='Погода')
    button3 = types.KeyboardButton(text='Ewelink')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    print(message)
    await message.reply(f"Здравствуй {message.from_user.first_name}, чем могу помочь?", reply_markup=keyboard)
    t = datetime.datetime.now().time().minute


# бан функция
@dp.message_handler(is_admin=True, commands=['ban'], commands_prefix='!/')
async def qwe(message: types.Message):

    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)


# функция для регистрации
@dp.message_handler(commands=['register'], commands_prefix='!/')
async def register(message: types.Message):
    global register, user
    user = message.from_user.id
    print(config.r)
    print(user)
    if message.chat.type == 'private':
        if str(user) in config.r:
            await message.reply('Вы уже зарегестрированны')
        else:
            register = True

            await message.reply('Для регистрации укажите свою электоронную почту.')


# функция обрабатывающая новых участников
@dp.message_handler(content_types=['new_chat_members'])
async def on_user_joined(message: types.Message):
    global timeout, c
    not_reg_user = message['new_chat_member']['id']

    if str(not_reg_user) in config.r:
        try:
            new_user = message['new_chat_member']['username']
            print(new_user)
            await message.reply(f'Здравствуй @{new_user}.')
        except:
            new_user = message['new_chat_member']['first_name']
            await message.reply(f'Здравствуй {new_user}.')
    else:
        print(message)
        print(not_reg_user)
        print(message)
        config.dont_reg.append(not_reg_user)
        try:
            new_user = message['new_chat_member']['username']
            print(new_user)
            await message.reply(f'Здравствуй @{new_user}, ты должен зарегестрироваться у @pythontest11101bot.\n'
                                f'После этого ты сможешь писать сообщения.')
        except:
            new_user = message['new_chat_member']['first_name']
            await message.reply(f'Здравствуй {new_user}, ты должен зарегестрироваться у @pythontest11101bot.\n'
                                f'После этого ты сможешь писать сообщения.')


@dp.callback_query_handler(text="Krasnodar")
async def krasnodar(call: types.CallbackQuery):
    cold = False
    warm = False
    mgr = config.owm.weather_manager()
    observation = mgr.weather_at_place('Краснодар')
    w = observation.weather
    temp = w.temperature('celsius')['temp']
    today = datetime.datetime.today()
    answer = 'Сегодня, ' + (
        today.strftime("%d/%m/%Y")) + ' ' + 'в городе ' + 'Краснодар' + ' ' + w.detailed_status + '\n'
    answer += 'Температура в районе ' + str(temp)[:2] + '℃' + '\n\n'
    if temp < 5:
        answer += 'Сейчас на улице холодно, одевайся тепло!'
        cold = True
    elif temp < 15:
        answer += 'Сейчас на улице прохладно, одевайся потеплее!'
        cold = True
    else:
        warm = True
        answer += 'Наулице тепло, одевайся как угодно!'
    otop = types.InlineKeyboardMarkup()
    otop.add(types.InlineKeyboardButton(text="Да", callback_data="Yes"))
    otop.add(types.InlineKeyboardButton(text="Нет", callback_data="No"))
    await call.message.answer(answer)
    if cold:
        if sonoff.devices[1]["status"] or sonoff.devices[2]['status'] or sonoff.devices[3]['status'] or\
                sonoff.devices[4]['status'] == 'off':

            await call.message.answer('Хотите включить отопление?\n'
                                    'Отопление по дому:\n'
                                    f'{sonoff.devices[1]["name"]}: {sonoff.devices[1]["status"]}\n'
                                    f'{sonoff.devices[2]["name"]}: {sonoff.devices[2]["status"]}\n'
                                    f'{sonoff.devices[3]["name"]}: {sonoff.devices[3]["status"]}\n'
                                    f'{sonoff.devices[4]["name"]}: {sonoff.devices[4]["status"]}', reply_markup=otop)
            await call.message.edit_reply_markup()
    if warm:
        if sonoff.devices[1]["status"] or sonoff.devices[2]['status'] or sonoff.devices[3]['status'] or\
                sonoff.devices[4]['status'] == 'on':
            await call.message.answer('Хотите выключить отопление?\n'
                                      'Отопление по дому:\n'
                                      f'{sonoff.devices[1]["name"]}: {sonoff.devices[1]["status"]}\n'
                                      f'{sonoff.devices[2]["name"]}: {sonoff.devices[2]["status"]}\n'
                                      f'{sonoff.devices[3]["name"]}: {sonoff.devices[3]["status"]}\n'
                                      f'{sonoff.devices[4]["name"]}: {sonoff.devices[4]["status"]}', reply_markup=otop)
            await call.message.edit_reply_markup()


@dp.callback_query_handler(text='Yes')
async def yes(call: types.CallbackQuery):
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.answer('Список девайсов:', reply_markup=clevhouse)
    await call.answer()


@dp.callback_query_handler(text='No')
async def no(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text='Moskow')
async def moscow(call: types.CallbackQuery):
    mgr = config.owm.weather_manager()
    observation = mgr.weather_at_place('Москва')
    w = observation.weather
    cold = False
    warm = False
    temp = w.temperature('celsius')['temp']
    today = datetime.datetime.today()
    answer = 'Сегодня, ' + (
        today.strftime("%d/%m/%Y")) + ' ' + 'в городе ' + 'Москва' + ' ' + w.detailed_status + '\n'
    answer += 'Температура в районе ' + str(temp)[:2] + '℃' + '\n\n'
    if temp < 5:
        cold = True
        answer += 'Сейчас на улице холодно, одевайся тепло!'
    elif temp < 15:
        cold = True
        answer += 'Сейчас на улице прохладно, одевайся потеплее!'
    else:
        warm = True
        answer += 'Наулице тепло, одевайся как угодно!'
    markup = types.ReplyKeyboardRemove()
    await call.message.answer(answer, reply_markup=markup)
    await call.message.edit_reply_markup()
    otop = types.InlineKeyboardMarkup()
    otop.add(types.InlineKeyboardButton(text="Да", callback_data="Yes"))
    otop.add(types.InlineKeyboardButton(text="Нет", callback_data="No"))
    if cold:
        if sonoff.devices[1]["status"] or sonoff.devices[2]['status'] or sonoff.devices[3]['status'] or\
                sonoff.devices[4]['status'] == 'off':

            await call.message.answer('Хотите включить отопление?\n'
                                    'Отопление по дому:\n'
                                    f'{sonoff.devices[1]["name"]}: {sonoff.devices[1]["status"]}\n'
                                    f'{sonoff.devices[2]["name"]}: {sonoff.devices[2]["status"]}\n'
                                    f'{sonoff.devices[3]["name"]}: {sonoff.devices[3]["status"]}\n'
                                    f'{sonoff.devices[4]["name"]}: {sonoff.devices[4]["status"]}', reply_markup=otop)
            await call.message.edit_reply_markup()
    if warm:
        if sonoff.devices[1]["status"] or sonoff.devices[2]['status'] or sonoff.devices[3]['status'] or\
                sonoff.devices[4]['status'] == 'on':
            await call.message.answer('Хотите выключить отопление?\n'
                                      'Отопление по дому:\n'
                                      f'{sonoff.devices[1]["name"]}: {sonoff.devices[1]["status"]}\n'
                                      f'{sonoff.devices[2]["name"]}: {sonoff.devices[2]["status"]}\n'
                                      f'{sonoff.devices[3]["name"]}: {sonoff.devices[3]["status"]}\n'
                                      f'{sonoff.devices[4]["name"]}: {sonoff.devices[4]["status"]}', reply_markup=otop)

            await call.message.edit_reply_markup()


# функция филитрации всех сообщений
@dp.message_handler()
async def filter_message(message: types.Message):
    global register, user, cod, body, gmail, keyboard, i, ewelink, msg
    print(message)
    if message.chat.type == 'supergroup':
        if str(message.from_user.id) not in config.r:
            await message.delete()
    if message.chat.type == 'private':
        if message.text == 'Курс доллара':
            if str(message.from_user.id) not in config.r:
                await message.reply('Вам надо зарегестрироваться')
            else:
                await message.reply(f'1$ = {str(USD)[:-3]}₽')

        elif message.text == 'Погода':

            pogoda = types.InlineKeyboardMarkup()
            pogoda.add(types.InlineKeyboardButton(text="Краснодар ", callback_data="Krasnodar"))
            pogoda.add(types.InlineKeyboardButton(text="Москва ", callback_data="Moskow"))
            if str(message.from_user.id) not in config.r:
                await message.reply('Вам надо зарегестрироваться')
            else:
                await message.answer("Из какого вы города?", reply_markup=pogoda)
        if message.text == 'Ewelink':
            if str(message.from_user.id) not in config.r:
                await message.reply('Вам надо зарегестрироваться')
            else:
                clevhouse = types.InlineKeyboardMarkup()
                for i in sonoff.devices:
                    clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

                msg = await message.answer('Список девайсов:', reply_markup=clevhouse)
                ewelink = True

        elif register == True:
            print(user)
            if '@' in message.text:
                gmail = message.text.lower()
                if message.from_user.id == user:
                    if gmail.lower() in config.gm:
                        email(message.text)
                        await message.reply('Введите код безопастноти который пришёл вам на электоронную почту.')
                        register = False
                        cod = True
                    else:
                        await message.reply('Вас нет в бд')


        elif cod:
            if message.text == str(body):
                cod = False
                bd(gmail, user)
                await message.reply('Вы успешно зарегистрировались.\n'
                                    'Вы можете войти в чат: https://t.me/+F9k0UQWiTPFjZGRi')
                if message.from_user.id in config.dont_reg:
                    index = config.dont_reg.index(message.from_user.id)
                    del config.r[index]
            else:
                await message.reply('Код не совпадает.')


@dp.callback_query_handler(text='1000b0eede')
async def update_results(call: types.CallbackQuery):
    global device, sonoff, msg
    devises.devace('1000b0eede', 0)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.message.edit_reply_markup()
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='100015971f')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('100015971f', 1)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='1000159a8b')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('1000159a8b', 2)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='1000159a6b')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('1000159a6b', 3)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='1000158eee')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('1000158eee', 4)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='1000159a85')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('1000159a85', 5)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='100014f8a5')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('100014f8a5', 6)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='10000d6500')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('10000d6500', 8)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


@dp.callback_query_handler(text='1000b0e462')
async def update_results(call: types.CallbackQuery):
    global device, sonoff
    devises.devace('1000b0e462', 7)
    sonoff = Sonoff(config.username, config.password, config.timezone, config.region)
    device = {}
    await call.answer()
    clevhouse = types.InlineKeyboardMarkup()
    for i in sonoff.devices:
        clevhouse.add(types.InlineKeyboardButton(text=i['name'] + ':' + i['status'], callback_data=i['deviceid']))

    await call.message.delete()
    await call.message.answer('Список девайсов:', reply_markup=clevhouse)


# функция отправляющая
def email(to):
    global body
    gmail_user = 'telebot288@gmail.com'
    gmail_password = 'ASDqwe123'

    sent_from = gmail_user

    subject = 'SUPER SECRET COD'
    body = random.randint(1000, 9999)
    print(body)

    email_text = f"""\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, "".join(to), subject, body)
    print("".join(to))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, "".join(to), email_text)
        server.close()
        print('Письмо отправленно')
    except:
        print('Ошибка')

# функция для записи в бд
def bd(gmail, user):
    con = sqlite3.connect("Telebot.sqlite")
    cur = con.cursor()
    result = cur.execute("""SELECT
           TELEGRAM
      FROM register;""").fetchall()
    for i in range(len(result)):
        config.r.append(result[i][0])
    sqlite_connection = sqlite3.connect('Telebot.sqlite')
    cursor = sqlite_connection.cursor()
    sql_update_query =f'''UPDATE register
   SET [INT] = 1,
   [TELEGRAM] = {str(user)}
 WHERE Email = '{gmail}';
'''
    cursor.execute(sql_update_query)
    sqlite_connection.commit()
    cursor.close()
    con = sqlite3.connect("Telebot.sqlite")
    cur = con.cursor()
    result = cur.execute("""SELECT
           TELEGRAM
      FROM register;""").fetchall()
    for i in range(len(result)):
        config.r.append(result[i][0])
    print(config.r)


if __name__ == '__main__':
    print(1)
    executor.start_polling(dp, skip_updates=True)