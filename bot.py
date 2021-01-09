import config
import logging
import db

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types

		# Подключение бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
db_w = db._db()

available_subjects = ["физика", "алгебра", "геометрия", "география", 
					  "химия", "биология", "ист. укр.", "всесв. ист.",
					  "укр. м.", "укр. лит.", "зар. лит.", "физра", "англ. м.", "информатика"]

		# Вывод инфы
@dp.message_handler(commands=['start'], state="*")
async def welcome(message: types.Message):
	sti = open('src/welcome_sti.webp', 'rb')
	await bot.send_sticker(message.chat.id, sti)
	await message.answer('Здраствуйте ' + str(message.from_user.first_name) + '!\nДля получения домашнего задания - /senddz\nДля получения помощи напишите - /help')

@dp.message_handler(commands=['help', 'h', '-h'], state="*")
async def help(message: types.Message):
	await message.answer('Доступные команды:\n/senddz - получить домашнее задание.\n'
		'/add_dz [Предмет] [Дата] [Домашка] - добавить домашнее задание\n/schedule - показать расписание\n'
		'/reg - зарегистрировать пользователя\n/verify [Код] - изменить статус пользователя')
	await message.answer("Доступные предметы: " + str(available_subjects))

@dp.message_handler(commands=['schedule'])
async def sched(message: types.Message):
	await message.answer("Понедельник:\n1. Физика\n2. Англ. м.\n3. Укр.м/Громад. осв.\n4. Укр. лит.\n\n"
		"Вторник:\n1. Ист. Укр.\n2. Информатика\n3. Алгебра\n4. -/Зар. лит.\n\n"
		"Среда:\n1. Физика\n2. Укр. м.\n3. Алгебра/Геометрия\n4. Химия/География\n\n"
		"Четверг:\n1. Биология/Всесв. ист.\n2. Физика\n3. Алгебра\n4. Англ. м.\n\n"
		"Пятница:\n1. Физра\n2. Алгебра\n3. Геометрия")

		# Работа с БД

# Регистрация пользователя
@dp.message_handler(commands=['reg'], state="*")
async def reg(message: types.Message):
	if (db_w.user_exists(message.from_user.id)):
		await message.answer("Вы уже зарегистрированы!")
	else:
		db_w.add_user(message.from_user.id, message.from_user.first_name)
		await message.answer("Вы успешно были зарегистрированы!")

# Подтверждение пользователя
@dp.message_handler(commands=['verify', 'ver', 'vrf', 'vf'], state="*")
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
class AddDz(StatesGroup):
	state_subj = State()
	state_date = State()
	state_hw = State()


@dp.message_handler(commands=['add_dz', 'adddz', 'addz'], state="*")
async def add_dz(message: types.Message):
	await message.answer("Введите предмет(Физика, Химия, Биология, ...):")
	if(db_w.check_status(message.from_user.id, 1)):
		await AddDz.state_subj.set()
	else:
		await message.answer("У вас недостаточно прав!")

@dp.message_handler(state = AddDz.state_subj)
async def add_dz_subj(message :types.Message, state = FSMContext):
	if message.text.lower() not in available_subjects:
		await message.reply("Недоступный предмет! Для получения полного списка предметов введите - /help")
		return
	else:
		await message.answer("Введите дату(YYYY-MM-DD, Пример: 2020-12-14):")
		await state.update_data(subject = message.text.lower())
		await AddDz.next()

@dp.message_handler(state = AddDz.state_date)
async def add_dz_date(message: types.Message, state=FSMContext):
	await state.update_data(date = message.text.lower())
	await message.answer("Введите домашнее задание: ")
	await AddDz.next()

@dp.message_handler(state = AddDz.state_hw)
async def add_dz_hw(message: types.Message, state=FSMContext):
	cur_state = await state.get_data()
	db_w.add_dz(cur_state['subject'], message.text, cur_state['date'])
	await message.answer("Домашнее задание было успешно добавлено!")
	await state.finish()

# Вывод домашнего задания
class SendDz(StatesGroup):
	state_subj = State()
	state_date = State()

@dp.message_handler(commands=['senddz', 'sentdz', 'senddd'], state="*")
async def send_dz(message: types.Message):
	await message.answer("Введите предмет(Физика, Химия, Биология, ...):")
	await SendDz.state_subj.set()

@dp.message_handler(state = SendDz.state_subj)
async def send_dz_subj(message: types.Message, state=FSMContext):
	if message.text.lower() not in available_subjects:
		await message.reply("Недоступный предмет! Для получения полного списка предметов введите - /help")
		return
	else:
		await message.answer("Введите дату(YYYY-MM-DD, Пример: 2020-12-14):")
		await state.update_data(subject = message.text.lower())
		await SendDz.next()

@dp.message_handler(state = SendDz.state_date)
async def send_dz_date(message: types.Message, state=FSMContext):
	subject = await state.get_data()
	await message.answer(db_w.find_dz(subject['subject'], message.text.lower()))
	await state.finish()
	
# Удаление домашнего задания
class DeleteDz(StatesGroup):
	state_subj = State()
	state_date = State()

@dp.message_handler(commands=['delete', 'del','deldz'], state="*")
async def del_dz(message: types.Message):
	await message.answer("Введите предмет(Физика, Химия, Биология, ...): ")
	await DeleteDz.state_subj.set()

@dp.message_handler(state = DeleteDz.state_subj)
async def del_dz_subj(message: types.Message, state=FSMContext):
	if message.text.lower() not in available_subjects:
		await message.reply("Недоступный предмет! Для получения полного списка предметов введите - /help")
		return
	else:
		await message.answer("Введите дату(YYYY-MM-DD, Пример: 2020-12-14):")
		await state.update_data(subject = message.text.lower())
		await DeleteDz.next()

@dp.message_handler(state = DeleteDz.state_date)
async def del_dz_date(message: types.Message, state=FSMContext):
	subject = await state.get_data()
	db_w.del_dz(subject['subject'], message.text.lower())
	await message.answer("Домашнее задание по " + subject['subject'] + " было успешно удалено!")
	await state.finish()

# Изминение домашнего задания
class ChangeDz(StatesGroup):
	state_subj = State()
	state_date = State()
	state_pre_final = State()
	state_final = State()

@dp.message_handler(commands=['change', 'chg','chg_dz'], state="*")
async def chg_dz(message: types.Message):
	await message.answer("Введите предмет(Физика, Химия, Биология, ...): ")
	await ChangeDz.state_subj.set()

@dp.message_handler(state = ChangeDz.state_subj)
async def chg_dz_subj(message: types.Message, state=FSMContext):
	if message.text.lower() not in available_subjects:
		await message.reply("Недоступный предмет! Для получения полного списка предметов введите - /help")
		return
	else:
		await message.answer("Введите дату(YYYY-MM-DD, Пример: 2020-12-14):")
		await state.update_data(subject = message.text.lower())
		await ChangeDz.next()

@dp.message_handler(state = ChangeDz.state_date)
async def chg_dz_date(message: types.Message, state=FSMContext):
	subject = await state.get_data()
	await message.answer(db_w.find_dz(subject['subject'], message.text.lower()) + "\nВы точно хотите его изменить?")
	await state.update_data(date = message.text.lower())
	await ChangeDz.next()

@dp.message_handler(state = ChangeDz.state_pre_final)
async def chg_dz_final(message: types.Message, state=FSMContext):
	if message.text.lower() in ['да', '1', 'д']:
		info = await state.get_data()
		await message.answer("Введите новое домашнее задание по " + info['subject'] + " за " + info['date'])
		await ChangeDz.next()
	else:
		await message.answer("Домашнее задание не было изменено!")
		await state.finish()

@dp.message_handler(state = ChangeDz.state_final)
async def chg_dz_final(message: types.Message, state=FSMContext):
	info = await state.get_data()
	db_w.change_dz(info['subject'], info['date'], message.text)
	await message.answer("Домашнее задание было успешно изменено!")
	await state.finish()


# На необработаеные случаи
@dp.message_handler()
async def er_mes(message: types.Message):
	await message.answer("Я вас не понимаю!")


if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)