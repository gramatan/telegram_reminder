# Telegram Reminder Bot

Этот проект представляет собой Telegram-бот, который отправляет задания пользователям в соответствии со списком заданий, загруженным из Google Sheets.
   - main.py - с использованием aiogram
   - ptb_main.py - с использованием Python-telegram-bot

## Установка

1. Клонируйте этот репозиторий на свой компьютер.
2. Установите необходимые зависимости, используя pip: `pip install -r requirements.txt`.
3. Создайте файл `config.py`, в котором укажите ваш Telegram Bot Token, как `TOKEN="YOUR_TELEGRAM_BOT_TOKEN"`.
4. Создайте сервисный аккаунт Google и скачайте файл `key.json`. Поместите этот файл в корневой каталог вашего проекта.

## Использование

1. Заполните Google Sheet следующим образом:
    - В первом столбце укажите ID пользователя Telegram, которому должно быть отправлено задание.
    - Во втором столбце укажите текст задания.
    - В третьем столбце укажите дату, когда задание должно быть отправлено.
    - В четвертом столбце укажите время, когда задание должно быть отправлено.
    - В пятом столбце укажите время в минутах, через которое будет проверяться статус задания.
2. Запустите бота, используя команду `python3 main.py`.
3. Отправьте команду `/start` от имени пользователя, который должен получить задание.
4. Менеджер может отправить задания всем пользователям, используя команду `/send_tasks`.

## Разработка

Бот разработан на Python, используя aiogram(main.py) или python-telegram-bot(ptb_main.py) для взаимодействия с API Telegram и gspread для работы с Google Sheets.