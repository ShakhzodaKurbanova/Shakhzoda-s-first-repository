import telebot
import buttons as bt
import database as db

# object bota
bot = telebot.TeleBot('7301005403:AAG0giN01norx0ixCID1RL13yyvgeMYw8XM')
# Временное хранилище данных
users = {}
admins = {}

# obrabotka starta


@bot.message_handler(commands=['start'])
def start_message(msg):
    user_id = msg.from_user.id
    check = db.check_user(user_id)
    pr_from_db = db.get_pr_id()

    if check:
        bot.send_message(user_id, 'Здравствуйте, добро пожаловать',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, "Выберите пункт меню:",
                         reply_markup=bt.main_menu(pr_from_db))
    else:
        bot.send_message(user_id, 'Здравствуйте, давайте начнем регистрацию!\n'
                                  'Введите свое имя')
        # переход на этап получения имени
        bot.register_next_step_handler(msg, get_name)

# этап получения имени


def get_name(msg):
    user_id = msg.from_user.id
    user_name = msg.text

    bot.send_message(user_id, 'Отлично! Теперь отправьте номер!',
                     reply_markup=bt.num_button())
    # переход на этап получения номера
    bot.register_next_step_handler(msg, get_number, user_name)


@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def choose_count(call):
    if call.data == 'increment':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=bt.choose_pr_count
                                      (db.get_exact_pr(users[call.message.message_id]['pr_name'])[4], 'increment',
                                       users[call.call.message.chat.id]['pr_amount']))
        users[call.call.message.chat.id]['pr_amount'] -= 1
    elif call.data == 'decrement':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=bt.choose_pr_count
                                      (db.get_exact_pr(users[call.message.message_id]['pr_name'])[4], 'decrement',
                                       users[call.call.message.chat.id]['pr_amount']))
        users[call.call.message.chat.id]['pr_amount'] -= 1
    elif call.data == 'to_cart':
        pr_name = db.get_exact_pr(users[call.call.message.chat.id]['pr_name'])[1]
        db.to_cart(call.message.chat.id, pr_name, users[call.message.chat.id]['pr_amount'])
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Товар успешно добавлен!\nЖелаете что-то еще?',
                         reply_markup=bt.main_menu(db.get_pr_id()))
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Перенаправлю вас обратно в меню:',
                         reply_markup=bt.main_menu(db.get_pr_id()))


# Корзина
@bot.callback_query_handler(lambda call: call.data in ['order', 'back', 'clear', 'cart'])
def cart_handle(call):
    text = 'Ваша корзина:\n\n'
    if call.data == 'clear':
        db.clear_cart(call.message.chat.id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Корзина очищена!')
        bot.send_message(call.message.chat.id, 'Перенаправлю вас обратно в меню:',
                         reply_markup=bt.main_menu(db.get_pr_id()))
    elif call.data == 'cart':
        user_cart = db.show_cart(call.message.chat.id)
        text = 'Ваша корзина:\n\n'
        total = 0.0
        for i in user_cart:
            text += (f'Товар: {i[1]}\n'
                     f'Количество: {i[2]}\n')
            total += db.get_pr_price(i[1])[0] * i[2]
        text += f'\nИтого: {total}'
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, text, reply_markup=bt.main_menu(db.get_pr_id()))
    elif call.data == 'order':
        text.replace('Ваша корзина:', 'Новый заказ')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Отправьте локацию для доставки',
                         reply_markup=bt.loc_button())
        # Переход на этап получения локации
        bot.register_next_step_handler(call, get_user_loc, text)
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Перенаправлю вас обратно в меню:',
                         reply_markup=bt.main_menu(db.get_pr_id()))
    elif call.data == 'cart':
        user_cart = db.show_cart(call.message.chat.id)
        text = 'Ваша корзина:\n\n'
        total = 0.0
        for i in user_cart:
            text += (f'Товар: {i[1]}\n'
                     f'Количество: {i[2]}\n')
            total += db.get_pr_price(i[1])[0] * i[2]
        text += f'\nИтого: {total}'
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, text, reply_markup=bt.main_menu(db.get_pr_id()))

# Этап получения локации


def get_user_loc(msg, text):
    user_id = msg.from_user.id
    if msg.location:
        text += f'Клиент: @{msg.from_user.username}'
        bot.send_message(-1234567890, text)
        bot.send_location(-1234567890, latitude=msg.location.latitude,
                          longitude=msg.location.longitude)
        db.make_order(user_id)
        bot.send_message(user_id, 'Ваш заказ был оформлен')
        bot.send_message(user_id, 'Выберите пункт ниже:',
                         reply_markup=bt.main_menu(db.get_pr_id()))
    else:
        bot.send_message(user_id, 'Отправьте локацию через кнопку')
        # Возврат на этап получения локации
        bot.register_next_step_handler(msg, get_user_loc, text)




def get_number(msg, user_name):
    user_id = msg.from_user.id

    if msg.contact:
        user_number = msg.contact.phone_number
        db.register(user_id, user_name, user_number)
        bot.send_message(user_id, 'Регистрация прошла успешно!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    # если пользователь отправил номер не по кнопке
    else:
        bot.send_message(user_id, 'Отправьте номер через кнопку!')
        # Возврат на этап получения номера
        bot.register_next_step_handler(msg, get_number, user_name)


@bot.callback_query_handler(lambda call: int(call.data) in [i[0] for i in db.get_all_pr()])
def choose_product(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    pr_info = db.get_exact_pr(call.data)
    bot.send_photo(call.message.chat.id, photo=pr_info[5],
                   caption=f'{pr_info[1]}\n\n'
                           f'Описание: {pr_info[2]}\n'
                           f'Цена: {pr_info[3]}\n'
                           f'Количество на складе: {pr_info[4]}',
                   reply_markup=bt.choose_pr_count(pr_info[4]))
    users[call.message.chat.id] = {'pr_name': call.data, 'pr_amount': 1}


# Админ панель ##
# Обработка команды /admin


@bot.message_handler(commands=['admin'])
def admin_message(msg):
    admin_id = 1234567890  # здесь айди админа
    if msg.from_user.id == admin_id:
        bot.send_message(admin_id, 'Выберите опцию:',
                         reply_markup=bt.admin_menu())
        # переход на этап выбора
        bot.register_next_step_handler(msg, admin_choice)
    else:
        bot.send_message(msg.from_user.id, 'Вы не админ!')

# Этап выбора


def admin_choice(msg):
    admin_id = 1234567890
    if msg.text == 'Добавить товар':
        bot.send_message(admin_id, 'Введите название продукта',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    elif msg.text == 'Удалить товар':
        if db.check_pr():
            bot.send_message(admin_id, 'Выберите продукт',
                             reply_markup=bt.admin_pr(db.get_pr_id()))
            # Переход на этап подтверждения удаления
            bot.register_next_step_handler(msg, confirm_delete)
        else:
            bot.send_message(admin_id, 'Продуктов в базе нет!')
            # Возвращение на этап выбора
            bot.register_next_step_handler(msg, admin_choice)
    elif msg.text == 'Изменить товар':
        if db.check_pr():
            bot.send_message(admin_id, 'Выберите продукт',
                             reply_markup=bt.admin_pr(db.get_pr_id()))
            # Переход на этап получения атрибута
            bot.register_next_step_handler(msg, get_pr_attr)
        else:
            bot.send_message(admin_id, 'Продуктов в базе нет!')
            # Возвращение на этап выбора
            bot.register_next_step_handler(msg, admin_choice)
    elif msg.text == 'В главное меню':
        pr_from_db = db.get_pr_id()
        bot.send_message(admin_id, 'Переотправляю вас обратно в гл меню',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(admin_id, 'Выберите пункт меню:',
                         reply_markup=bt.main_menu(pr_from_db))

# Этап получения названия


def get_pr_name(msg):
    admin_id = 1234567890
    pr_name = msg.text
    bot.send_message(admin_id, 'Теперь введите описание')
    # Переход на этап получения описания
    bot.register_next_step_handler(msg, get_pr_des, pr_name)

# Этап получения описания


def get_pr_des(msg, pr_name):
    admin_id = 1234567890
    pr_name = msg.text
    bot.send_message(admin_id, 'Теперь введите количество товара')
    # Переход на этап получения количества
    bot.register_next_step_handler(msg, get_pr_count, pr_name)

# Этап получения колличества


def get_pr_count(msg, pr_name, pr_des):
    admin_id = 1234567890
    if msg.text.isnumeric():
        pr_count = int(msg.text)
        bot.send_message(admin_id, 'Теперь введите цену товара')
        # Переход на этап получения количества
        bot.register_next_step_handler(msg, get_pr_price, pr_name, pr_des, pr_count)
    else:
        bot.send_message(admin_id, 'Пишите только целые числа!')
        # Возврат на этап получения кол-ва
        bot.register_next_step_handler(msg, get_pr_count, pr_name, pr_des)

# Этап получения цены


def get_pr_price(msg, pr_name, pr_des, pr_count):
    admin_id = 1234567890
    if msg.text.isdectimal():
        pr_price = float(msg.text)
        bot.send_message(admin_id, 'Перейдите на сайт https://postimages.org/. \n'
                         'Загрузите фото товара и отправьте прямую на него ссылку!')
        # Переход на этап получения фото
        bot.register_next_step_handler(msg, get_pr_photo, pr_name, pr_des, pr_count, pr_price)

# Этап получения фото


def get_pr_photo(msg, pr_name, pr_des, pr_count, pr_price):
    admin_id = 1234567890
    pr_photo = msg.text
    db.pr_to_db(pr_name, pr_des, pr_price, pr_count, pr_photo)
    bot.send_message(admin_id, 'Товар успешно добавлен! Желаете что-то еще?',
                     reply_markup=bt.admin_menu())
    # Переход на этап получения выбоа
    bot.register_next_step_handler(msg, admin_choice)

# Этап подтверждения удаления


def confirm_delete(msg):
    admin_id = admin_id = 1234567890
    pr_name = msg.text
    bot.send_message(admin_id, 'Вы точно уверены?',
                     reply_markup=bt.confirm_buttons())
    # Переход на этап получения ответа
    bot.register_next_step_handler(msg, delete_product, pr_name)


# Этап получения ответа
def delete_product(msg, pr_name):
    admin_id = 1234567890
    if msg.text == 'Да':
        db.del_pr(pr_name)
        bot.send_message(admin_id, 'Товар успешно удален!',
                         reply_markup=bt.admin_menu())
        # Переход на этап выбора
        bot.register_next_step_handler(msg, admin_choice)
    elif msg.text == 'Нет':
        bot.send_message(admin_id, 'Отменено',
                         reply_markup=bt.admin_menu())
        # Переход на этап выбора
        bot.register_next_step_handler(msg, admin_choice)

# Этап выбора атрибута


def get_pr_attr(msg):
    admin_id = 1234567890
    admins[admin_id] = msg.text
    bot.send_message(admin_id, 'Какой атрибут продукта хотите изменить?',
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.send_message(admin_id, 'Выберите фтрибут ниже',
                     reply_markup=bt.change_buttons())


@bot.callback_query_handler(lambda call: call.data in ['name', 'des', 'price', 'photo', 'back'])
def change_attr(call):
    if call.data == 'name':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите новое название продукта')
        attr = call.data
        # Переход на этап подтверждения изменения
        bot.register_next_step_handler(call, confirm_change, attr)
    elif call.data == 'des':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите новое описание продукта')
        attr = call.data
        # Переход на этап подтверждения изменения
        bot.register_next_step_handler(call, confirm_change, attr)
    elif call.data == 'price':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите новую цену продукта')
        attr = call.data
        # Переход на этап подтверждения изменения
        bot.register_next_step_handler(call, confirm_change, attr)
    elif call.data == 'photo':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Введите ссылку на новое фото продукта')
        attr = call.data
        # Переход на этап подтверждения изменения
        bot.register_next_step_handler(call, confirm_change, attr)
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, 'Перенаправляю вас обратно в меню',
                         reply_markup=bt.admin_menu())
        # Переход на этап выбора
        bot.register_next_step_handler(call, admin_choice)

# Этап подтверждения изменения


def confirm_change(msg, attr):
    admin_id = 1234567890
    new_value = msg.text
    if attr == 'price':
        db.change_pr_attr(admins[admin_id], float(new_value), attr=attr)
    else:
        db.change_pr_attr(admins[admin_id], new_value, attr=attr)
    bot.send_message(admin_id, 'Изменение прошло успешно!',
                     reply_markup=bt.admin_menu())
    # Переход на этап выбора
    bot.register_next_step_handler(msg, admin_choice)


# Запуск бота

bot.polling()
