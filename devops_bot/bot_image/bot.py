import os
import re
import logging
import paramiko
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Настройка логгирования
logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def send_out(update, output):
    if len(output) > 4096:
        for x in range(0, len(output), 4096):
            update.message.reply_text(output[x:x+4096])
    else:
        if len(output) == 0:
            update.message.reply_text("Пустой результат")
        else:
            update.message.reply_text(output)

# Функция обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}! Я бот для поиска информации, проверки паролей и мониторинга Linux системы.')

# Функция обработки команды /help
def helpCommand(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/get_repl_logs - вывод логов о репликации\n'
                              +'/get_emails - вывод данных из таблиц о email-адресах\n'
                              +'/get_phone_numbers - вывод данных из таблиц о номерах телефона\n'
                              +'/find_email - поиск email в тексте\n'
                              +'/find_phone_number - поиск телефонных номеров в тексте'
                              + '\n/verify_password - определение сложности пароля\n/get_release - информация о релизе'
                              + '\n/get_uname - информация об архитектуры процессора, имени хоста системы и версии ядра'
                              + '\n/get_uptime - информация о времени работы'
                              + '\n/get_df - информация о состоянии файловой системы'
                              + '\n/get_free - информация о состоянии оперативной памяти'
                              + '\n/get_mpstat - информация о производительности системы'
                              + '\n/get_w - информация о работающих в данной системе пользователях'
                              + '\n/get_auths - информация о последних 10 входах в систему'
                              + '\n/get_critical - информация о последних 5 критических события'
                              + '\n/get_ps - информация о запущенных процессах'
                              + '\n/get_ss - информация об используемых портах'
                              + '\n/get_apt_list - информации об установленных пакетах'
                              + '\n/get_services - информации о запущенных сервисах')


def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')

    return 'findEmails'

def findEmails(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    EmailRegex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    # ([\w\.-]+@([\w-]+\.)+[\w-]{2,4})
    EmailList = EmailRegex.findall(user_input) # Ищем номера телефонов

    if not EmailList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Email не найдены')
        return ConversationHandler.END  # Завершаем диалог
    
    EmailNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(EmailList)):
        EmailNumbers += f'{i+1}. {EmailList[i]}\n' # Записываем очередной номер
    context.user_data['emails'] = EmailList
    EmailNumbers += "Хотите записать их в базу данных? (да/нет)"    
    update.message.reply_text(EmailNumbers) # Отправляем сообщение пользователю
    return 'insert_email_in_db'


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(\+7\d{10}|\+7\(\d{3}\)\d{7}|\+7 \(\d{3}\) \d{3} \d{2} \d{2}|\+7 \d{3} \d{3} \d{2} \d{2}|\+7-\d{3}-\d{3}-\d{2}-\d{2}|8\d{10}|8\(\d{3}\)\d{7}|8 \(\d{3}\) \d{3} \d{2} \d{2}|8 \d{3} \d{3} \d{2} \d{2}|8-\d{3}-\d{3}-\d{2}-\d{2}|8 \(\d{3}\) \d{3}-\d{2}-\d{2}|8\(\d{3}\)\d{3}-\d{2}-\d{2}|\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}|\+7\(\d{3}\)\d{3}-\d{2}-\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем диалог
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
    context.user_data['phone_numbers'] = phoneNumberList
    phoneNumbers += "Хотите записать их в базу данных? (да/нет)"    
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    return 'insert_phone_in_db'  # Переходим к состоянию insert_phone_in_db

def insert_email_in_db(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()
    if user_response == 'да':
        # Получаем сохраненные номера телефонов из контекста
        emails = context.user_data.get('emails', [])
        if emails:
            output = sql_insert(emails, False)
            update.message.reply_text(output)
    else:
        update.message.reply_text("Операция добавления отменена.")
    
    return ConversationHandler.END  # Завершаем диалог

def insert_phone_in_db(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()
    if user_response == 'да':
        # Получаем сохраненные номера телефонов из контекста
        phone_numbers = context.user_data.get('phone_numbers', [])
        if phone_numbers:
            output = sql_insert(phone_numbers, True)
            update.message.reply_text(output)
    else:
        update.message.reply_text("Операция добавления отменена.")
    
    return ConversationHandler.END  # Завершаем диалог

def VerifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'VerifyPassword'

# Функция для проверки сложности пароля
def VerifyPassword(update: Update, context: CallbackContext):
    password = update.message.text
    if re.match(r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()]).{8}', password):
        update.message.reply_text("Пароль сложный.")
    else:
        update.message.reply_text("Пароль простой.")

    return ConversationHandler.END # Завершаем работу обработчика диалога

# Функция для установления SSH-подключения и выполнения команды на удаленном сервере
def ssh_command(command):
    try:
        HOST = os.getenv("RM_HOST")
        PORT = os.getenv("RM_PORT")
        USER = os.getenv("RM_USER")
        PASSWORD = os.getenv("RM_PASSWORD")
        logging.info(f"(hostname={HOST}, username={USER}, password={PASSWORD}, port={PORT})")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        output = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return output
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с SSH: %s", error)
        return "Ошибка при работе с SSH. Проверьте Виртуальную машину и правильность переменных"


# Функция для получения информации о релизе
def get_release(update, context):
    output = ssh_command('lsb_release -a')
    send_out(update, output)

# Функция для получения информации об архитектуре процессора, имени хоста системы и версии ядра
def get_uname(update, context):
    output = ssh_command('uname -a')
    send_out(update, output)

# Функция для получения информации о времени работы
def get_uptime(update, context):
    output = ssh_command('uptime')
    send_out(update, output)
    
# Функция для получения информации о состоянии файловой системы. 
def get_df(update, context):
    output = ssh_command('df -h')
    send_out(update, output)

# Функция для получения информации о состоянии оперативной памяти. 
def get_free(update, context):
    output = ssh_command('free -h')
    send_out(update, output)

# Функция для получения информации о производительности системы
def get_mpstat(update, context):
    output = ssh_command('mpstat')
    send_out(update, output)

# Функция для получения информации о работающих в данной системе пользователях
def get_w(update, context):
    output = ssh_command('w')
    send_out(update, output)

# Функция для сбора информации о последних 10 входах в систему 
def get_auths(update, context):
    output = ssh_command('last -n 10')
    send_out(update, output)

# Функция для сбора информации о последних 5 критических событиях
def get_critical(update, context):
    output = ssh_command('journalctl -p crit -n 5')
    send_out(update, output)

# Функция для сбора информации о запущенных процессах
def get_ps(update, context):
    output = ssh_command('ps aux')
    send_out(update, output)

# Функция для сбора информации об используемых портах
def get_ss(update, context):
    output = ssh_command('ss -tuln')
    send_out(update, output)

# Функция для сбора информации об установленных пакетах
def get_apt_list(update: Update, context: CallbackContext) -> None:
    command = 'dpkg -l'
    if context.args:
        package_name = ' '.join(context.args)
        command += f' | grep {package_name}'
    output = ssh_command(command)
    send_out(update, output)

# Функция для сбора информации о запущенных сервисах
def get_services(update, context):
    output = ssh_command('systemctl list-units --type=service')
    send_out(update, output)

# Обработчик команды /get_repl_logs
def get_repl_logs(update: Update, context: CallbackContext) -> None:
    # Проверка доступа к файлу логов
    log_file_path = '/var/log/postgresql/postgresql.log'
    if not os.path.exists(log_file_path):
        update.message.reply_text('Логи о репликации не найдены.')
        return
    
    # Отправка содержимого лог-файла в сообщении
    with open(log_file_path, 'r') as file:
        log_content = file.readlines()
        log_filtered = [x for x in log_content if "repl" in x]
        log_filtered = "".join(x for x in log_filtered)
        send_out(update, log_filtered)

def sql_select(table):
    connection = None
    result_messages = ''
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT, 
                                    database=DB_DATABASE)

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        data = cursor.fetchall()
        for i in range(len(data)):
            result_messages += f'{i+1}. {data[i][1]}\n' 

        if len(result_messages) == 0:
            result_messages = 'No values'
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        result_messages = "Error"
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return result_messages
    
def sql_insert(values, flag):
    connection = None
    result_messages = None
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT, 
                                    database=DB_DATABASE)

        cursor = connection.cursor()
        if flag == True:
            for value in values:
                cursor.execute(f"INSERT INTO phone_numbers (phone_number) VALUES ('{value}');")
        else:
            for value in values:
                cursor.execute(f"INSERT INTO emails (email) VALUES ('{value}');")
        connection.commit()
        result_messages = 'Success'
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        result_messages = "Error"
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return result_messages
    
def get_emails(update: Update, context: CallbackContext) -> None:
    output = sql_select('emails')
    send_out(update, output)

def get_phone_numbers(update: Update, context: CallbackContext) -> None:
    output = sql_select('phone_numbers')
    send_out(update, output)


# Функция для обработки неизвестных команд
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Извините, я не понимаю эту команду.")

def main() -> None:
    TOKEN = os.getenv("TG_TOKEN")
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # Обработчик номеров
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'insert_phone_in_db': [MessageHandler(Filters.text & ~Filters.command, insert_phone_in_db)],
        },
        fallbacks=[]
    )
    # Обработчик email
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'insert_email_in_db': [MessageHandler(Filters.text & ~Filters.command, insert_email_in_db)],
        },
        fallbacks=[]
    )
    # Обработчик паролей
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', VerifyPasswordCommand)],
        states={
            'VerifyPassword': [MessageHandler(Filters.text & ~Filters.command, VerifyPassword)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list, pass_args=True))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

	
    # Регистрируем обработчик дял неизвестных комманд
    dp.add_handler(MessageHandler(Filters.command, unknown))

	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    try:
        # Попытка загрузить переменные окружения из файла .env
        load_dotenv()
        main()
    except FileNotFoundError:
        print("Файл .env не найден")
    except Exception as e:
        print(f"Ошибка при загрузке .env: {e}")
