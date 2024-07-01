import sqlite3
from datetime import date

def read_sqlite_table():
    try:
        sqlite_connection = sqlite3.connect('statistick.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        #Check USD
        sqlite_select_query = """SELECT * from USD"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        #print("Всего строк:  ", len(records))
        #print("Вывод каждой строки")
        print("USD: ")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        #Check EURO
        sqlite_select_query = """SELECT * from EURO"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        # print("Всего строк:  ", len(records))
        # print("Вывод каждой строки")
        print("EURO")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        #Check Tenge
        sqlite_select_query = """SELECT * from Tenge"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк:  ", len(records))
        print("Вывод каждой строки")
        print("Tenge")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        # Check London_USD
        sqlite_select_query = """SELECT * from London_USD"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк:  ", len(records))
        print("Вывод каждой строки")
        print("London_USD")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        # Check London_EURO
        sqlite_select_query = """SELECT * from London_EURO"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк:  ", len(records))
        print("Вывод каждой строки")
        print("London_EURO")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        # Check London_Tenge
        sqlite_select_query = """SELECT * from London_Tenge"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Всего строк:  ", len(records))
        print("Вывод каждой строки")
        print("London_Tenge")
        for row in records:
            print("date: ", row[0])
            print("Course: ", row[1])

        cursor.execute("SELECT * from USD")
        all_USD = cursor.fetchall()
        print(all_USD)


        cursor.execute("SELECT * from USD")
        all_USD = cursor.fetchall()
        print(all_USD)

        # cur_date = "2024-05-09"
        #
        # cursor.execute("SELECT Course from USD WHERE date = ?",(cur_date,))
        # records = cursor.fetchall()
        # print(records)
        #
        # if records:
        #     print("Yes")
        # else:
        #     print("No")
        # to_konv = "USD"
        # sqlite_select_query = f"""SELECT Course from {to_konv}"""
        # cursor.execute(sqlite_select_query)
        # records = cursor.fetchall()
        # print("I get next data: ", records[-1][0])

        sqlite_connection.commit()  #
        cursor.close()  # Отключаем курсор
        sqlite_connection.close()  # Отключаемся от БД

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

read_sqlite_table()