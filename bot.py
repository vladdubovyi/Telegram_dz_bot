import config
import logging
import db

from aiogram import Bot, Dispatcher, executor, types

		# Подключение бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot=bot)
db_w = db._db()

		# Вывод инфы
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
	sti = open('src/welcome_sti.webp', 'rb')
	await bot.send_sticker(message.chat.id, sti)
	await message.answer('Здраствуйте ' + str(message.from_user.first_name) + '!\nДля получения домашнего задания - /senddz [Предмет] [Дата]\nДля получения помощи напишите - /help')

@dp.message_handler(commands=['help', 'h', '-h'])
async def help(message: types.Message):
	await message.answer('Доступные команды:\n/senddz [Предмет] [Дата] - получить домашнее задание.\n'
		'/add_dz [Предмет] [Дата] [Домашка] - добавить домашнее задание\n/schedule - показать расписание\n'
		'/reg - зарегистрировать пользователя\n/verify [Код] - изменить статус пользователя')

@dp.message_handler(commands=['schedule'])
async def sched(message: types.Message):
	await message.answer("Понедельник:\n1. Физика\n2. Англ. м.\n3. Укр.м/Громад. осв.\n4. Укр. лит.\n\n"
		"Вторник:\n1. Ист. Укр.\n2. Информатика\n3. Алгебра\n4. -/Зар. лит.\n\n"
		"Среда:\n1. Физика\n2. Укр. м.\n3. Алгебра/Геометрия\n4. Химия/География\n\n"
		"Четверг:\n1. Биология/Всесв. ист.\n2. Физика\n3. Алгебра\n4. Англ. м.\n\n"
		"Пятница:\n1. Физра\n2. Алгебра\n3. Геометрия")

		# Работа с БД
# Вывод домашки
@dp.message_handler(commands=['senddz', 'sentdz', 'sentddd'])
async def send_dz(message: types.Message):
	command = message.text
	command = command.split()
	if len(command) != 3:
		await message.answer("Неверная запись!\nПример: /senddz Физика 2020-12-14")
	else:
		subj = command[1]
		date = command[2]
		await message.answer(db_w.find_dz(subj, date))

# Регистрация пользователя
@dp.message_handler(commands=['reg'])
async def reg(message: types.Message):
	if (db_w.user_exists(message.from_user.id)):
		await message.answer("Вы уже зарегистрированы!")
	else:
		db_w.add_user(message.from_user.id, message.from_user.first_name)
		await message.answer("Вы успешно были зарегистрированы!")

# Подтверждение пользователя
@dp.message_handler(commands=['verify', 'ver', 'vrf', 'vf'])
async def verify(message: types.Message):
	command = message.text
	command = command.split()
	if len(command) != 2:
		await message.answer("Неверная запись!\n")
	else:
		if(command[1] == "123321PoAsd"):
			await message.answer(db_w.set_status(message.from_user.id, 1))
		else:
			await message.answer("Введен неправильный код!")

# Добавление домашнего задания
@dp.message_handler(commands=['add_dz', 'adddz', 'addz'])
async def add_dz(message: types.Message):
	if(db_w.check_status(message.from_user.id, 1)):
		command = message.text
		command = command.split()
		if len(command) == 4 or len(command) == 3:
			subj = command[1]
			date = command[2]
			homework_text = command[3]
			db_w.add_dz(subj, homework_text, date)
			await message.answer("Домашнее задание было успешно добавлено!")
		else:
			await message.answer("Неверная запись!\nПример: /add_dz Физика 2020-12-14 #12.13-12.21")
	else:
		await message.answer("У вас недостаточно прав!")


# На необработаеные случаи
@dp.message_handler()
async def er_mes(message: types.Message):
	await message.answer("Я вас не понимаю!")



if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)