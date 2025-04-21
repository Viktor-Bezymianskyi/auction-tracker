# Auction Tracker Tool

## Description

**Auction Tracker Tool** is a tool for monitoring, analyzing, and collecting public data from Yahoo! JAPAN Auctions. The application is designed for personal use to track lots, analyze bidding history, and calculate average prices for various items on auctions.

This project is implemented using Python and the official Yahoo! JAPAN Auctions API.

## Features

- **Lot parsing:** Retrieve a list of lots based on keywords or categories.
- **Price analysis:** Calculate the average price of lots.
- **Bid tracking:** Track bidding history and get notifications when a bid is outbid.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/auction-tracker.git
   cd auction-tracker

2. **Install dependencies:**

    ```To work with the project, you need to install Python libraries:
    pip install -r requirements.txt

    ```The requirements.txt file usually contains libraries such as:

    requests — for making HTTP requests.

    beautifulsoup4 — for parsing HTML.

    pandas — for working with data (if needed).

3. **Register on Yahoo! JAPAN Developer Network:**
    ```To use the API, you need to register an application on the Yahoo! JAPAN Developer Network. Obtain the App ID and Client Secret, which need to be specified in the code.

    Example of registration: see this section.

4.  **API Setup:**
    ```Create a .env file to store confidential data:
    YAHOO_APP_ID=your_app_id
    YAHOO_CLIENT_SECRET=your_client_secret

5.  **Run:**
    ```To run the project, execute:
    python main.py
    This will launch the main script for parsing auction data.

**Usage**

Lot search: To start parsing lots, specify keywords or a category in the request.

    ``Example of searching lots by keywords:
    search_results = yahoo_api.search_auctions('laptop')

**Price analysis: Calculate the average price for the found lots:**

    average_price = analyze_average_price(search_results)

**Development**

    If you want to make changes to the project or propose improvements, please follow these steps:

    1. Fork the repository.

    2. Create a new branch for your feature (git checkout -b feature-name).

    3. Make changes and submit a Pull Request.

    License
    This project is licensed under the MIT License. For more details, see LICENSE.


# Auction Tracker Tool

## Описание

**Auction Tracker Tool** — это инструмент для мониторинга, анализа и сбора публичных данных с аукционов Yahoo! JAPAN. Приложение предназначено для личного использования, чтобы отслеживать лоты, анализировать историю ставок и рассчитывать средние цены для различных товаров на аукционах.

Этот проект реализован с использованием Python и официального API Yahoo! JAPAN для аукционов.

## Функции

- **Парсинг лотов:** Получение списка лотов по ключевым словам или категориям.
- **Анализ цен:** Рассчёт средней цены лотов.
- **Трекинг ставок:** Отслеживание истории ставок и уведомлений при перебитии ставки.

## Установка

1. **Клонировать репозиторий:**

   ```bash
   git clone https://github.com/yourusername/auction-tracker.git
   cd auction-tracker 

2. **Установить зависимости:**

    ```Для работы с проектом необходимо установить библиотеки Python:
    pip install -r requirements.txt

    ```В requirements.txt обычно содержатся библиотеки, такие как:

    requests — для выполнения HTTP-запросов.

    beautifulsoup4 — для парсинга HTML.

    pandas — для работы с данными (если нужно).

3. **Регистрация в Yahoo! JAPAN Developer Network:**
    ```Для использования API вам необходимо зарегистрировать приложение на Yahoo! JAPAN Developer Network. Получите App ID и Client Secret, которые нужно будет указать в коде.

    Пример регистрации: см. в этом разделе.

4.  **Настройка API:**
    ```Создайте файл .env для хранения конфиденциальных данных:
    YAHOO_APP_ID=your_app_id
    AHOO_CLIENT_SECRET=your_client_secret

5.  **Запуск:**
    ```Чтобы запустить проект, выполните:
    python main.py
    Это запустит основной скрипт для парсинга данных с аукционов.

**Использование**

Поиск лотов: Чтобы начать парсить лоты, укажите ключевые слова или категорию в запросе.

    ``Пример поиска лотов по ключевым словам:
    search_results = yahoo_api.search_auctions('laptop')

**Анализ цен: Рассчитать среднюю цену для найденных лотов:**

    average_price = analyze_average_price(search_results)

**Разработка**

```Если вы хотите внести изменения в проект или предложить улучшения, пожалуйста, следуйте этим шагам:

1. Форкните репозиторий.

2. Создайте новую ветку для вашей фичи (git checkout -b feature-name).

3. Сделайте изменения и отправьте Pull Request.

Лицензия
Этот проект лицензирован по лицензии MIT. Для подробной информации см. LICENSE.