import sqlite3

conn = sqlite3.connect(r"C:\\Users\\nasty\\Practicum_2kurs\\ImageBinarization\\DB.db")  # замени путь на реальный
cursor = conn.cursor()

# Посмотреть все таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Таблицы:", tables)

# Проверить, есть ли таблица users и что в ней
if ('users',) in tables:
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print("Структура таблицы users:")
    for col in columns:
        print(col)
else:
    print("Таблица 'users' не найдена.")

conn.close()
