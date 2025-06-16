import sqlite3

def get_data():
  connection = sqlite3.connect("database/Personal.db")
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM records LIMIT 10")
  data = cursor.fetchall()
  connection.close()
  return data