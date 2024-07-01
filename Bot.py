import telebot
import webbrowser
from telebot import types
import sqlite3
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import date
from requests.exceptions import ConnectionError, RequestException
from datetime import datetime, timedelta

bot = telebot.TeleBot("6474521787:AAFZhyohoin1HnsB4cWTU2aA3Bwysbbt8Lg")#Токен бота



@bot.message_handler(commands=['start']) #При вводе боту команды /start
def main(message):
    try:
        """Создание баз данных и отправление пользователю приветственного сообщения"""
        connection = sqlite3.connect('statistick.db') #Подключаемся к БД
        cursor = connection.cursor() #Создаем объект курсор для выполнения запросов
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS USD (date TEXT ,course REAL)''') #Если еще не существует, то создаем таблицу для статистики доллара(Дата YYYY-MM-DD) (ЦЕНТРОБАНК)
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS EURO (date TEXT ,course REAL)''')  #Если еще не существует, то создаем таблицу для статистики Евро(Дата YYYY-MM-DD) (ЦЕНТРОБАНК)
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS Tenge (date TEXT ,course REAL)''')  #Если еще не существует, то создаем таблицу для статистики Тенге(Дата YYYY-MM-DD) (ЦЕНТРОБАНК)

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS London_USD (date TEXT ,course REAL)''')  # Если еще не существует, то создаем таблицу для статистики доллара(Дата YYYY-MM-DD) (ЛОНДОНСКИЙ МЕЖДУНАРОДНЫЙ БАНК)
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS London_EURO (date TEXT ,course REAL)''')  # Если еще не существует, то создаем таблицу для статистики Евро(Дата YYYY-MM-DD) (ЛОНДОНСКИЙ МЕЖДУНАРОДНЫЙ БАНК)
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS London_Tenge (date TEXT ,course REAL)''')  # Если еще не существует, то создаем таблицу для статистики Тенге(Дата YYYY-MM-DD) (ЛОНДОНСКИЙ МЕЖДУНАРОДНЫЙ БАНК)

        connection.commit() #
        cursor.close() #Отключаем курсор
        connection.close() #Отключаемся от БД
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}, Команды: "
                                          f"1)/conversion: Конвертация валюты; 2)/Current_stat: курс на сегодняшний день; 3)/statForCertDay: Статистика за определенный день, начиная от 2024-05-07; 4)/statForPeriod: Статистика за какой-то временной период, минимальный курс, максимальный курс, средний курс")#Отправляем пользователю сообщение
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    # finally:
    #     if sqlite_connection:
    #         sqlite_connection.close()
    #         print("Соединение с SQLite закрыто")

def UpdateStatictick():
    """Обновляем текущие курсы валют и заносим в БД"""
    try:
        print("The data update process")
        connection = sqlite3.connect('statistick.db')  # Подключаемся к БД
        cursor = connection.cursor()  # Создаем объект курсор для выполнения запросов

        cur_date = str(date.today()) #Получаем сегодняшнюю дату

        usd_rate = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='USD']/Value").text.replace(",", ".")
        ) #Подключаемся к XML файлу Центробанка с текщим курсом валют, находим статистику по USD, вытаскиваем текущий курс. Меняем в числе "," на "."

        usd_nominal = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='USD']/Nominal").text.replace(",", ".")
        ) #Извлекаем из файла номинал, на который нужно поделить курс, чтобы получить курс на 1 рубль

        cursor.execute("INSERT INTO USD (date,course) VALUES ('%s','%s')" % (
            cur_date, usd_rate / usd_nominal)) #Добавляем в таблицу USD сегодняшнюю дату и курс доллара, деленный на номинал

        euro_rate = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='EUR']/Value").text.replace(",", ".")
        )#Подключаемся к XML файлу Центробанка с текщим курсом валют, находим статистику по Euro, вытаскиваем текущий курс. Меняем в числе "," на "."

        euro_nominal = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='EUR']/Nominal").text.replace(",", ".")
        ) #Извлекаем из файла номинал, на который нужно поделить курс, чтобы получить курс на 1 рубль

        cursor.execute("INSERT INTO EURO (date,course) VALUES ('%s','%s')" % (
            cur_date, euro_rate / euro_nominal))  # Добавляем в таблицу EURO сегодняшнюю дату и курс Евро, деленный на номинал

        tenge_rate = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='KZT']/Value").text.replace(",", ".")
        ) #Подключаемся к XML файлу Центробанка с текщим курсом валют, находим статистику по Tenge, вытаскиваем текущий курс. Меняем в числе "," на "."

        tenge_nominal = float(
            ET.fromstring(requests.get("https://www.cbr.ru/scripts/XML_daily.asp").text).find(
                "./Valute[CharCode='KZT']/Nominal").text.replace(",", ".")
        ) #Извлекаем из файла номинал, на который нужно поделить курс, чтобы получить курс на 1 рубль

        cursor.execute("INSERT INTO Tenge (date,course) VALUES ('%s','%s')" % (
            cur_date, tenge_rate/tenge_nominal))  # Добавляем в таблицу tenge сегодняшнюю дату и курс Тенге, деленный на номинал

        usd_rate_London = get_currency_rate("https://www.google.com/search?q=курс+доллара+к+рублю") #Используя функцию get_currency_rate получаем курс доллара с Лондонского меж. банка

        cursor.execute("INSERT INTO London_USD (date,course) VALUES ('%s','%s')" % (
            cur_date, usd_rate_London))  # Добавляем в таблицу Lonon_USD сегодняшнюю дату и курс USD, деленный на номинал

        euro_rate_London = get_currency_rate("https://www.google.com/search?q=курс+евро+к+рублю")

        cursor.execute("INSERT INTO London_EURO (date,course) VALUES ('%s','%s')" % (
            cur_date, euro_rate_London))

        tenge_rate_London = get_currency_rate("https://www.google.com/search?q=курс+тенге+к+рублю")

        cursor.execute("INSERT INTO London_Tenge (date,course) VALUES ('%s','%s')" % (
            cur_date, tenge_rate_London))

        # connection.commit()  #
        # cursor.close()  # Отключаем курсор
        # connection.close()  # Отключаемся от БД

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if connection:
            connection.commit()  #
            cursor.close()  # Отключаем курсор
            connection.close()  # Отключаемся от БД
            print("Соединение с SQLite закрыто")

def get_currency_rate(url):
    """Ф-ция для универсального получения курса валюты с Лондонского международного банка"""
    # Адрес сайта, с которого мы будем получать данные

    # Получаем содержимое страницы
    response = requests.get(url)

    # Создаем объект BeautifulSoup для парсинга HTML-разметки
    soup = BeautifulSoup(response.content, "html.parser")

    # Получаем элемент с курсом валюты
    result = soup.find("div", class_="BNeawe iBp4i AP7Wnd").get_text()

    # Возвращаем курс валюты как число
    return float(result.replace(",", ".").split()[0])

@bot.message_handler(commands=['conversion']) #При вводе боту команды /conversion
def KonvertToHelper(message):
    """Запрашиваем у пользователя данные и переходим с этими данными в основную функцию конвертации валюты"""
    bot.send_message(message.chat.id, f"Введите через пробел валюту из которой конвертировать, валюту в которую конвертировать и сумму. Доступные валюты: RUB: Рубль; USD: доллар; EURO: Евро; Tenge: Тенге. Конвертация происходит по курсу Центробанка")
    bot.register_next_step_handler(message, KonvertTo)

def KonvertTo(message):
    """Конвертируем сумму по запросу пользователя: [ВалютаИзКоторойКОнвертируем ВалютаВКотороуюКонвертируем Сумма]"""
    try:
        connection = sqlite3.connect('statistick.db')  # Подключаемся к БД
        cursor = connection.cursor()  # Создаем объект курсор для выполнения запросов

        message_mas = message.text.strip().split() #Преобразуем строку в массив
        from_konv = message_mas[0] #Получаем валюту из которой конвертируем
        to_konv = message_mas[1] #Получаем валюту в которую конвертируем
        sum_konv = float(message_mas[2]) #Сумма конвертирования
        if from_konv != "USD" and from_konv != "EURO" and from_konv != "Tenge" and from_konv != "RUB":
            bot.send_message(message.chat.id,
                             f"Введенна некорректная валюта из которой конвертируем")
        elif to_konv != "USD" and to_konv != "EURO" and to_konv != "Tenge" and to_konv != "RUB":
            bot.send_message(message.chat.id,
                             f"Введенна некорректная валюта в которую конвертируем")
        else:

            if from_konv == to_konv:
                bot.send_message(message.chat.id,
                                 f"Сумма конвертации из {from_konv} в {to_konv} = {sum_konv}") #Если Валюта из которой конвертируем равна той, в которую конвертируем, то просто возращаем введенную пользователем сумму без изменений

            elif from_konv == "RUB":
                sqlite_select_query = f"""SELECT Course from {to_konv}""" #Извлекаем из БД Курс валюты введенной пользователем
                cursor.execute(sqlite_select_query) #Выполняем запрос
                records = cursor.fetchall() #Получаем число записей в виде упорядоченного списка
                equel_sum = sum_konv / records[-1][0] #Делим сумму на самый свежий курс валюты(Находится на последней позиции в БД)
                bot.send_message(message.chat.id,
                                 f"Сумма конвертации из {from_konv} в {to_konv} = {equel_sum}") #Выводим пользователю вычисленное значение

            elif to_konv == "RUB":
                sqlite_select_query = f"""SELECT Course from {from_konv}"""  # Извлекаем из БД Курс валюты введенной пользователем
                cursor.execute(sqlite_select_query)  # Выполняем запрос
                records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
                equel_sum = sum_konv * records[-1][0]  # В этот раз умножаем сумму на самый свежий курс валюты(Находится на последней позиции в БД)(В БД курс записан относительно рубля)
                bot.send_message(message.chat.id,
                                 f"Сумма конвертации из {from_konv} в {to_konv} = {equel_sum}")  # Выводим пользователю вычисленное значение

            elif from_konv != "RUB" and to_konv != "RUB":
                sqlite_select_query = f"""SELECT Course from {from_konv}"""  # Извлекаем из БД Курс валюты введенной пользователем
                cursor.execute(sqlite_select_query)  # Выполняем запрос
                records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
                equel_sum_helper = sum_konv * records[-1][0]  # Вычисляем промежуточное значение от текущей валюты в рубль

                sqlite_select_query = f"""SELECT Course from {to_konv}"""  # Извлекаем из БД Курс валюты введенной пользователем
                cursor.execute(sqlite_select_query)  # Выполняем запрос
                records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
                equel_sum = equel_sum_helper / records[-1][0]  # Делим промежуточное значение на курс желаемой валюты
                bot.send_message(message.chat.id,
                                 f"Сумма конвертации из {from_konv} в {to_konv} = {equel_sum}")  # Выводим пользователю вычисленное значение

            else: bot.send_message(message.chat.id, "Введены некорректные данные")

        # connection.commit()  #
        # cursor.close()  # Отключаем курсор
        # connection.close()  # Отключаемся от БД

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса, проверьте корректность введенных данных")

    finally:
        if connection:
            connection.commit()  #
            cursor.close()  # Отключаем курсор
            connection.close()  # Отключаемся от БД
            print("Соединение с SQLite закрыто")

@bot.message_handler(commands=['Current_stat']) #При вводе боту команды /Current_stat
def CurStat(message):
    """Выводим текущий курс существующих в БД валют"""

    try:
        connection = sqlite3.connect('statistick.db')  # Подключаемся к БД
        cursor = connection.cursor()  # Создаем объект курсор для выполнения запросов

        sqlite_select_query = f"""SELECT Course from USD"""  # Извлекаем из БД Курс доллара
        cursor.execute(sqlite_select_query)  # Выполняем запрос
        records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
        cur_USD = records[-1][0]  # получаем самый свежий курс доллара(Находится на последней позиции в БД)

        sqlite_select_query = f"""SELECT Course from EURO"""  # Извлекаем из БД Курс ЕВРО
        cursor.execute(sqlite_select_query)  # Выполняем запрос
        records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
        cur_EURO = records[-1][0]  # получаем самый свежий курс ЕВРО(Находится на последней позиции в БД)

        sqlite_select_query = f"""SELECT Course from Tenge"""  # Извлекаем из БД Курс Тенге
        cursor.execute(sqlite_select_query)  # Выполняем запрос
        records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
        cur_Tenge = records[-1][0]  # получаем самый свежий курс Тенге(Находится на последней позиции в БД)

        sqlite_select_query = f"""SELECT Course from London_USD"""  # Извлекаем из БД Курс доллара
        cursor.execute(sqlite_select_query)  # Выполняем запрос
        records = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка
        cur_London_USD = records[-1][0]  # получаем самый свежий курс доллара Лондонского меж. банка(Находится на последней позиции в БД)

        sqlite_select_query = f"""SELECT Course from London_EURO"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cur_London_EURO = records[-1][0]

        sqlite_select_query = f"""SELECT Course from London_Tenge"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cur_London_Tenge = records[-1][0]

        bot.send_message(message.chat.id,f"Текущая статистика курса: Центробанк: [USD: {cur_USD}; EURO: {cur_EURO}; Tenge: {cur_Tenge}];\n Лондонский межгосударственный банк: [USD: {cur_London_USD}; EURO: {cur_London_EURO}; Tenge: {cur_London_Tenge}]")#Выводим сообщение

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,"Что-то пошло не так, повторите запрос позже")

    finally:
        if connection:
            connection.commit()  #
            cursor.close()  # Отключаем курсор
            connection.close()  # Отключаемся от БД
            print("Соединение с SQLite закрыто")


@bot.message_handler(commands=['statForCertDay']) #При вводе боту команды /statForCertDay
def StatForCerDayHelper(message):
    """Запрашиваем у пользователя за какой день он бы хотел получить статистику и переходим с этим сообщением в основную функцию"""
    try:
        bot.send_message(message.chat.id,f"Введите дату, за которую вы бы хотели получить статистику следующим образом: YYYY-MM-DD. Например: 2024-05-07. Статистика по центробанку собирается от 2024-05-07; по Лондонскому межгосударственному банку от 2024-05-12")
        bot.register_next_step_handler(message, StatForCerDay)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Что-то пошло не так, повторите запрос позже")

def StatForCerDay(message):
    """Получаем статистику за выбранный пользователем день"""
    try:
        connection = sqlite3.connect('statistick.db')  # Подключаемся к БД
        cursor = connection.cursor()  # Создаем объект курсор для выполнения запросов

        cur_date = message.text.strip() #Получаем введенное пользователем сообщение

        if cur_date[0:4] != "2024" or cur_date[4] != "-" or int(cur_date[5:7]) > 12 or cur_date[7] != "-" or int(cur_date[8:]) > 31: #Проверям, что пользователь корректно ввел дату
            raise Exception("Введена некорректная дата") #Если есть ошибка, то принудительно вызываем исключение

        cursor.execute("SELECT Course from USD WHERE date = ?", (cur_date,)) #Извлекаем из БД курс доллара по выбранной дате
        cur_USD = cursor.fetchall() # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT Course from EURO WHERE date = ?",(cur_date,))  # Извлекаем из БД курс Евро по выбранной дате
        cur_EURO = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT Course from Tenge WHERE date = ?",(cur_date,))  # Извлекаем из БД курс Тенге по выбранной дате
        cur_Tenge = cursor.fetchall()  # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT Course from London_USD WHERE date = ?",
                       (cur_date,))
        cur_London_USD = cursor.fetchall()

        cursor.execute("SELECT Course from London_EURO WHERE date = ?",
                       (cur_date,))
        cur_London_EURO = cursor.fetchall()

        cursor.execute("SELECT Course from London_Tenge WHERE date = ?",
                       (cur_date,))
        cur_London_Tenge = cursor.fetchall()

        if cur_USD:
            bot.send_message(message.chat.id,f"Статистика по Центробанку за {cur_date}: USD: {cur_USD[0][0]}; EURO: {cur_EURO[0][0]}; Tenge: {cur_Tenge[0][0]}")
        else:
            bot.send_message(message.chat.id,f"Извините, но за текущую дату нет данных по Центробанку")

        if cur_London_USD:
            bot.send_message(message.chat.id,f"Статистика по Лондонскому межгосударственному банку за {cur_date}: USD: {cur_London_USD[0][0]}; EURO: {cur_London_EURO[0][0]}; Tenge: {cur_London_Tenge[0][0]}")
        else:
            bot.send_message(message.chat.id, f"Извините, но за текущую дату нет данных по Лондонскому межгосударственному банку")
        # connection.commit()  #
        # cursor.close()  # Отключаем курсор
        # connection.close()  # Отключаемся от БД
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса, проверьте корректность введенных данных")
    finally:
        if connection:
            connection.commit()  #
            cursor.close()  # Отключаем курсор
            connection.close()  # Отключаемся от БД
            print("Соединение с SQLite закрыто")

@bot.message_handler(commands=['statForPeriod']) #При вводе боту команды /statForPeriod
def StatForPeriodHelper(message):
    """Запрашиваем у пользователя за какой период он бы хотел получить статистику и переходим с этим сообщением в основную функцию"""
    try:
        bot.send_message(message.chat.id,f"Введите период, за который вы бы хотели получить статистику следующим образом: YYYY-MM-DD - YYYY-MM-DD. Например: 2024-05-07 - 2024-05-08")
        bot.register_next_step_handler(message, StatForPeriod)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Что-то пошло не так, повторите запрос позже")

def StatForPeriod(message):
    """Получение статистики за выбранный пользователем период"""
    try:
        #LIST INDEX OUT OF RANGE
        connection = sqlite3.connect('statistick.db')  # Подключаемся к БД
        cursor = connection.cursor()  # Создаем объект курсор для выполнения запросов

        cur_date = message.text.strip().split()  # Получаем введенное пользователем сообщение
        first_date = cur_date[0] #Получаем начальную дату из сообщения
        last_date = cur_date[-1] #Получаем конечную дату из сообщения

        if first_date[0:4] != "2024" or first_date[4] != "-" or int(first_date[5:7]) > 12 or first_date[7] != "-" or int(first_date[8:]) > 31: #Проверям, что пользователь корректно ввел дату
            raise Exception("Введена некорректная дата") #Если есть ошибка, то принудительно вызываем исключение

        if last_date[0:4] != "2024" or last_date[4] != "-" or int(last_date[5:7]) > 12 or last_date[7] != "-" or int(last_date[8:]) > 31: #Проверям, что пользователь корректно ввел дату
            raise Exception("Введена некорректная дата") #Если есть ошибка, то принудительно вызываем исключение

        if first_date != last_date:
            first_date_date = datetime.strptime(first_date, "%Y-%m-%d") #Преобразуем строку в тип datetime (Тип для работы с датами)
            last_date_date = datetime.strptime(last_date, "%Y-%m-%d") #Преобразуем строку в тип datetime (Тип для работы с датами)
            amount_days = last_date_date - first_date_date #Вычисляем кол-во дней м/у последней датой и первой
            cur_date = first_date_date #Текущая дата, в начале устанавливаем начальную дату
            all_days = [] #Создаем пустой массив, для дальнейшего добавления в него дат
            for i in range(0, amount_days.days + 1): #Цикл от 0 до кол-ва дней (включительно последний день)
                all_days.append(cur_date) #Добавляем в массив каждый день, начиная от начального, заканчивая дальнейшим
                cur_date = cur_date + timedelta(days=1) #Добавляем 1 день к текущей дате

        cursor.execute("SELECT * from USD") #Извлекаем все данные из таблицы USD
        all_USD = cursor.fetchall() # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT * from EURO") #Извлекаем все данные из таблицы EURO
        all_EURO = cursor.fetchall() # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT * from Tenge") #Извлекаем все данные из таблицы Tenge
        all_Tenge = cursor.fetchall() # Получаем число записей в виде упорядоченного списка

        cursor.execute("SELECT * from London_USD")
        all_London_USD = cursor.fetchall()

        cursor.execute("SELECT * from London_EURO")
        all_London_EURO = cursor.fetchall()

        cursor.execute("SELECT * from London_Tenge")
        all_London_Tenge = cursor.fetchall()

        #Центробанк
        all_cur_usd = [] #Создаем пустой список, в который будем складывать все курсы доллара за период
        all_cur_EURO = []  # Создаем пустой список, в который будем складывать все курсы евро за период
        all_cur_Tenge = []  # Создаем пустой список, в который будем складывать все курсы тенге за период

        #Лондонский межгосударственный банк
        all_cur_London_usd = []
        all_cur_London_EURO = []
        all_cur_London_Tenge = []

        for i in all_days: #Внешний цикл по дням, за период введенным пользователем, от начального, до последнего
            for j in range(0, len(all_USD)): #Внутренний цикл по элементам из списков валют с базы данных(можно использовать вместо all_USD: all_EURO и all_Tenge, это не играет роли, тк они одной размерности)
                if i == datetime.strptime(all_USD[j][0], "%Y-%m-%d"): #Если текущая дата периода, введенного пользователем равна текущей дате из all_USD(Перед сравнением преобразуем в тип date)
                    all_cur_usd.append(all_USD[j][1])
                    all_cur_EURO.append(all_EURO[j][1])
                    all_cur_Tenge.append(all_Tenge[j][1])
                    break #Далее нет смысла делать сравнения, покидаем внутренний цикл
            for k in range(0, len(all_London_USD)):
                if i == datetime.strptime(all_London_USD[k][0], "%Y-%m-%d"):
                    all_cur_London_usd.append(all_London_USD[k][1])
                    all_cur_London_EURO.append(all_London_EURO[k][1])
                    all_cur_London_Tenge.append(all_London_Tenge[k][1])
                    break

        if all_cur_usd: #Если список не пустой, то данные за этот период есть, продолжаем собирать статистику
            min_USD = all_cur_usd[0] #добавляем статистику минимального курса из периода
            max_USD = all_cur_usd[0] #добавляем статистику максимального курса из периода
            acc = 0  # Аккумулятор для суммирования
            for i in all_cur_usd:
                if i > max_USD:
                    max_USD = i
                if i < min_USD:
                    min_USD = i
                acc += i  # В all_cur_usd хранятся данные вида [[int], [int]], что усложняет применение метода sum, поэтому суммируем вручную, используя аккумулятор
            average_USD = acc / len(all_cur_usd) #Вычисляем среднее по курсу из периода

            min_EURO = all_cur_EURO[0]  # добавляем статистику минимального курса из периода
            max_EURO = all_cur_EURO[0]  # добавляем статистику максимального курса из периода
            acc = 0  # Аккумулятор для суммирования
            for i in all_cur_EURO:
                if i > max_EURO:
                    max_EURO = i
                if i < min_EURO:
                    min_EURO = i
                acc += i  # В all_cur_usd хранятся данные вида [[int], [int]], что усложняет применение метода sum, поэтому суммируем вручную, используя аккумулятор
            average_EURO = acc / len(all_cur_EURO)  # Вычисляем среднее по курсу из периода


            min_Tenge = all_cur_Tenge[0]  # добавляем статистику минимального курса из периода
            max_Tenge = all_cur_Tenge[0]  # добавляем статистику максимального курса из периода
            acc = 0  # Аккумулятор для суммирования
            for i in all_cur_Tenge:
                if i > max_Tenge:
                    max_Tenge = i
                if i < min_Tenge:
                    min_Tenge = i
                acc += i  # В all_cur_usd хранятся данные вида [[int], [int]], что усложняет применение метода sum, поэтому суммируем вручную, используя аккумулятор
            average_Tenge = acc / len(all_cur_Tenge)  # Вычисляем среднее по курсу из периода
            bot.send_message(message.chat.id,
                             f"Статистика за период от {first_date} до {last_date} по Центробанку: USD: min = {min_USD}, max = {max_USD}, average = {average_USD}; EURO: min = {min_EURO}, max = {max_EURO}, average = {average_EURO}; Tenge: min = {min_Tenge}, max = {max_Tenge}, average = {average_Tenge}")

        else:
            bot.send_message(message.chat.id, f"За данный период нет данных по Центробанку")

        #Лондонский меж.банк

        if all_cur_London_usd:
            min_London_USD = all_cur_London_usd[0]
            max_London_USD = all_cur_London_usd[0]
            acc = 0
            for i in all_cur_London_usd:
                if i > max_London_USD:
                    max_London_USD = i
                if i < min_London_USD:
                    min_London_USD = i
                acc += i
            average_London_USD = acc / len(all_cur_London_usd)


            min_London_EURO = all_cur_London_EURO[0]
            max_London_EURO = all_cur_London_EURO[0]
            acc = 0
            for i in all_cur_London_EURO:
                if i > max_London_EURO:
                    max_London_EURO = i
                if i < min_London_EURO:
                    min_London_EURO = i
                acc += i
            average_London_EURO = acc / len(all_cur_London_EURO)

            min_London_Tenge = all_cur_London_Tenge[0]
            max_London_Tenge = all_cur_London_Tenge[0]
            acc = 0
            for i in all_cur_London_Tenge:
                if i > max_London_Tenge:
                    max_London_Tenge = i
                if i < min_London_Tenge:
                    min_London_Tenge = i
                acc += i
            average_London_Tenge = acc / len(all_cur_London_Tenge)

            bot.send_message(message.chat.id,f"Статистика за период от {first_date} до {last_date} по Лондонскому Межгосударственному банку: USD: min = {min_London_USD}, max = {max_London_USD}, average = {average_London_USD}; "
                                             f"EURO: min = {min_London_EURO}, max = {max_London_EURO}, average = {average_London_EURO}; Tenge: min = {min_London_Tenge}, max = {max_London_Tenge}, average = {average_London_Tenge}")

        else:
            bot.send_message(message.chat.id,f"За данный период нет данных по Лондонскому межгосударственному банку")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Что-то пошло не так, проверьте корректность введенных данных")
    finally:
        if connection:
            connection.commit()  #
            cursor.close()  # Отключаем курсор
            connection.close()  # Отключаемся от БД
            print("Соединение с SQLite закрыто")

#Если в текущий день не было обновления данных по курсу, то обновляем
try:
    sqlite_connection = sqlite3.connect('statistick.db') #Подключаемся к БД
    cursor = sqlite_connection.cursor() #Создаем курсор
    sqlite_select_query = """SELECT date from USD""" #Извлекаем дату из таблицы USD
    cursor.execute(sqlite_select_query) #Выполняем запрос выше
    records = cursor.fetchall() #Получаем число записей в виде упорядоченного списка
    if str(date.today()) != records[-1][0]: #Сравниваем текущую дату с датой в конце БД, которая является последней
        UpdateStatictick() #Если условие выполнено, вызываем функцию по обновлению статистики
    else:
        print("Data was update today") #Иначе выводим сообщение в консоль

    sqlite_connection.commit()  #
    cursor.close()  # Отключаем курсор
    sqlite_connection.close()  # Отключаемся от БД
except sqlite3.Error as error:
    print("Ошибка при работе с SQLite", error)
# finally:
#     if sqlite_connection:
#         sqlite_connection.close()
#         print("Соединение с SQLite закрыто")
try:
    bot.polling(none_stop=True) #Чтобы программа не остановилась сразу же после запуска
except (telebot.apihelper.ApiException, RequestException) as e:
    pass #Если бот бездействует какое-то время, то программа завершается аварийно, последними 2-мя строками решаем эту проблему