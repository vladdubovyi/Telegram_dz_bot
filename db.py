import mysql.connector
from datetime import datetime 


# Работа с бд
class _db:

	def __init__(self):
		# Подключение к бд
		self.db = mysql.connector.connect(
			host = "localhost",
			user = "root",  
			passwd = "", 
			database = "Homework" # Название базы
			)
		# Иниацилизация курсора
		self.cur = self.db.cursor()

	#Нахождение дз по предмету и дате
	def find_dz(self, subj, date):
		self.cur.execute("SELECT Homework_text FROM homework WHERE Subject = %s AND Date = %s", (subj, date))
		res = self.cur.fetchone()		
		if res == None:
			return "Ничего не найдено по запросу " + subj + " " + date
		else:
			return "Домашнее задание по " + subj + " за " + date + ": " + str(res)

	# Проверка на существование пользователя
	def user_exists(self, userId):
		self.cur.execute("SELECT * FROM users WHERE UserId = " + str(userId))
		res = self.cur.fetchone()
		if res == None:
			return False
		else:
			return True

	# Добавление нового пользователя
	def add_user(self, userId, userName):
		self.cur.execute("INSERT INTO users(UserId, Date_of_registration, FirstName) VALUES (%s, %s, %s)", (userId, datetime.now(), userName))
		self.db.commit()

	# Изменение статуса
	def set_status(self, userId, status):
		if(self.user_exists(userId)):
			self.cur.execute("UPDATE users SET status = %s WHERE UserId = %s", (str(status), str(userId)))
			self.db.commit()
			return "Статус был успешно изменен!"
		else:
			return "Сначала зарегестрируйтесь! /reg"

	# Проверка статуса
	def check_status(self, userId, status):
		self.cur.execute("SELECT * FROM users WHERE status = %s AND UserId = %s", (str(status), str(userId)))
		res = self.cur.fetchone()
		if res == None:
			return False
		else:
			return True

	# Добавление домашнего задания
	def add_dz(self, subject, homework, date = datetime.now()):
		self.cur.execute("INSERT INTO homework(Subject, Homework_text, Date) VALUES (%s, %s, %s)", (subject, homework, date))
		self.db.commit()
	
	# Удаление домашнего задания	
	def del_dz(self, subject, date):
		self.cur.execute("DELETE FROM homework WHERE Subject = %s AND Date = %s", (subject, date))
		self.db.commit()

	# Изменение домашнего задания
	def change_dz(self, subject, date, homework_text):
		self.del_dz(subject, date)
		self.add_dz(subject, homework_text, date) 