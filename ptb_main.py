import logging
import gspread
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, ApplicationBuilder
from oauth2client.service_account import ServiceAccountCredentials
import asyncio

from config import TOKEN

logging.basicConfig(level=logging.INFO)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
client = gspread.authorize(creds)
sheet = client.open('test-telegram-reminder').sheet1


manager_chat_id = '123160759'   # change it to your manager tg id.
task_status = {}


async def start(update: Update, context: CallbackContext):
    tel_id = str(update.message.from_user.id)
    records = sheet.get_all_records()

    for i, record in enumerate(records, start=2):
        if tel_id == str(record['tel_id']):
            text = record['text']
            answer_time = record['answer_time']

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Выполнено", callback_data='done')],
                [InlineKeyboardButton("Не сделано", callback_data='not_done')]
            ])

            await context.bot.send_message(chat_id=tel_id, text=text, reply_markup=keyboard)
            task_status[tel_id] = 'pending'
            logging.info(f'Sent task to user {tel_id}')
            sheet.update_cell(i, 6, 'отправлено пользователю')
            asyncio.create_task(check_response(tel_id, int(answer_time)))


async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    task_status[query.from_user.id] = query.data
    await context.bot.send_message(chat_id=manager_chat_id, text=f"User {query.from_user.id} selected {query.data}")


async def manager_send_tasks(update: Update, context: CallbackContext):
    if update.message.from_user.id == int(manager_chat_id):
        records = sheet.get_all_records()

        for i, record in enumerate(records, start=2):
            tel_id = record['tel_id']
            text = record['text']
            answer_time = record['answer_time']

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Выполнено", callback_data='done')],
                [InlineKeyboardButton("Не сделано", callback_data='not_done')]
            ])

            try:
                await context.bot.send_message(chat_id=tel_id, text=text, reply_markup=keyboard)
                task_status[tel_id] = 'pending'
                logging.info(f'Sent task to user {tel_id}')
                sheet.update_cell(i, 6, 'отправлено пользователю')
                asyncio.create_task(check_response(tel_id, int(answer_time)))
            except Exception as e:
                logging.error(f'Error while sending task to user {tel_id}: {e}')


async def check_response(tel_id, answer_time):
    await asyncio.sleep(answer_time * 60)

    if task_status[tel_id] == 'pending':
        await app.bot.send_message(chat_id=manager_chat_id, text=f"Пользователь {tel_id} не отреагировал вовремя")


# TG bot instance
app = ApplicationBuilder().token(TOKEN).build()

start_handler = CommandHandler('start', start)
button_callback_handler = CallbackQueryHandler(button_callback, pattern='^(done|not_done)$')
manager_send_tasks_handler = CommandHandler('send_tasks', manager_send_tasks)
app.add_handler(start_handler)
app.add_handler(button_callback_handler)
app.add_handler(manager_send_tasks_handler)


def main():
    app.run_polling()


if __name__ == '__main__':
    main()
