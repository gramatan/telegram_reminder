import asyncio
import logging

import gspread

from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN


# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


# Google Sheets Auth
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
client = gspread.authorize(creds)

sheet = client.open('test-telegram-reminder').sheet1

# TG bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


manager_chat_id = '123160759'  # ID менеджера

task_status = {}  # Сохраняем таски тут


@dp.message_handler(commands='start')
async def send_task(message: types.Message):
    tel_id = str(message.from_user.id)
    records = sheet.get_all_records()

    for i, record in enumerate(records, start=2):
        if tel_id == str(record['tel_id']):
            text = record['text']
            answer_time = record['answer_time']

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Выполнено", callback_data='done'))
            keyboard.add(types.InlineKeyboardButton("Не сделано", callback_data='not_done'))

            await bot.send_message(chat_id=tel_id, text=text, reply_markup=keyboard)

            task_status[tel_id] = 'pending'
            logging.info(f'Sent task to user {tel_id}')

            sheet.update_cell(i, 6, 'отправлено пользователю')

            asyncio.create_task(check_response(tel_id, int(answer_time)))


@dp.callback_query_handler(lambda c: c.data and c.data in ['Готово', 'Провалено'])
async def button_callback(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)

    await bot.edit_message_text(chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                text=f"Selected option: {query.data}")
    task_status[query.from_user.id] = query.data

    await bot.send_message(chat_id=manager_chat_id, text=f"User {query.from_user.id} selected {query.data}")

@dp.message_handler(commands='send_tasks')
async def manager_send_tasks(message: types.Message):
    if message.from_user.id == int(manager_chat_id):    # проверка на менеджера
        records = sheet.get_all_records()

        for i, record in enumerate(records, start=2):
            tel_id = record['tel_id']
            text = record['text']
            answer_time = record['answer_time']

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Выполнено", callback_data='done'))
            keyboard.add(types.InlineKeyboardButton("Не сделано", callback_data='not_done'))

            try:
                await bot.send_message(chat_id=tel_id, text=text, reply_markup=keyboard)

                task_status[tel_id] = 'pending'
                logging.info(f'Sent task to user {tel_id}')

                sheet.update_cell(i, 6, 'отправлено пользователю')  # не в условиях задачи. для отладки

                asyncio.create_task(check_response(tel_id, int(answer_time)))
            except Exception as e:
                logging.error(f'Error while sending task to user {tel_id}: {e}')


async def check_response(tel_id, answer_time):
    await asyncio.sleep(answer_time * 60)

    if task_status[tel_id] == 'pending':
        await bot.send_message(chat_id=manager_chat_id, text=f"Пользователь {tel_id} не отреагировал вовремя")

if __name__ == '__main__':
    executor.start_polling(dp)