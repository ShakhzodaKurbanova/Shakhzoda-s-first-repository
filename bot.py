import telebot
import buttons as bt
import database as db

# object bota
bot = telebot.TeleBot('7301005403:AAG0giN01norx0ixCID1RL13yyvgeMYw8XM')

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


## Админ панель ##
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
        else:
            bot.send_message(admin_id, 'Продуктов в базе нет!')
            # Возвращение на этап выбора
            bot.register_next_step_handler(msg, admin_choice)
    elif msg.text == 'Изменить товар':
        if db.check_pr():
            bot.send_message(admin_id, 'Выберите продукт',
                             reply_markup=bt.admin_pr(db.get_pr_id()))
        else:
            bot.send_message(admin_id, 'Продуктов в базе нет!')
            # Возвращение на этап выбора
            bot.register_next_step_handler(msg, admin_choice)

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
    bot.register_next_step_handler(msg, get_pr_count, pr_name, pr_des)

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

# Запуск бота


bot.polling()
