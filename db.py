import sqlite3

connection = sqlite3.connect("data.db")
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS macbook (name TEXT, price INTEGER, quantity INTEGER, discount INTEGER)"
cursor.execute(create_table)

connection.commit()
connection.close()
