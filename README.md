# Yahoo Auctions Parser

## Описание проекта (Русский)
Этот проект предназначен для парсинга данных с Yahoo Auctions (Японские аукционы) и экспорта их в CSV или Google Sheets. Основные функции:

1. **Парсинг лотов**: Извлечение информации о товарах (название, цена, количество ставок, продавец и т.д.).
2. **Поддержка прокси**: Ротация прокси для обхода ограничений.
3. **Экспорт данных**: Сохранение результатов в CSV или загрузка в Google Sheets.
4. **Модульность**: Отдельные файлы для обработки CSV, извлечения статусов, количества и исключений.
5. **Режим отладки**: Генерация HTML-файлов для анализа ошибок.

### Установка
1. Клонируйте репозиторий:
   ```bash
   git clone <ваш-репозиторий>
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Скопируйте `.env.example` в `.env` и заполните его настройками:
   ```bash
   cp .env.example .env
   ```

### Дополнительные настройки
- **Прокси**: Убедитесь, что прокси-серверы активны и доступны. Пример заполнения `.env`:
  ```env
  PROXY_1=http://user:pass@ip:port
  PROXY_2=http://user:pass@ip:port
  PROXY_SOCKS5=socks5://user:pass@ip:port
  ```
- **User-Agent**: Добавьте несколько User-Agent'ов для ротации:
  ```env
  USER_AGENT_1=Mozilla/5.0 (...)
  USER_AGENT_2=Mozilla/5.0 (...)
  ```
- **Google Sheets**: Для экспорта в Google Sheets настройте API и укажите ID таблицы в `.env`:
  ``` env
# Google Sheets integration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_EMAIL=your_email@.com

# Currency conversion
YEN_TO_EUR=165  # Exchange rate
  ```

### Использование
Запустите основной скрипт:
```bash
python parse_auctions.py
```

---

## Project Description (English)
This project is designed for parsing data from Yahoo Auctions (Japanese auctions) and exporting it to CSV or Google Sheets. Key features:

1. **Lot Parsing**: Extracting product information (title, price, bids, seller, etc.).
2. **Proxy Support**: Proxy rotation to bypass restrictions.
3. **Data Export**: Saving results to CSV or uploading to Google Sheets.
4. **Modularity**: Separate files for CSV processing, status extraction, quantity, and exclusions.
5. **Debug Mode**: Generating HTML files for error analysis.

### Installation
1. Clone the repository:
   ```bash
   git clone <your-repository>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure it:
   ```bash
   cp .env.example .env
   ```

### Additional Configuration
- **Proxies**: Ensure proxies are active and accessible. Example `.env` setup:
  ```env
  PROXY_1=http://user:pass@ip:port
  PROXY_2=http://user:pass@ip:port
  PROXY_SOCKS5=socks5://user:pass@ip:port
  ```
- **User-Agents**: Add multiple User-Agents for rotation:
  ```env
  USER_AGENT_1=Mozilla/5.0 (...)
  USER_AGENT_2=Mozilla/5.0 (...)
  ```
- **Google Sheets**: For Google Sheets export, configure the API and specify the sheet ID in `.env`:
  ``` env
# Google Sheets integration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_EMAIL=your_email@.com

# Currency conversion
YEN_TO_EUR=165  # Exchange rate
  ```

### Usage
Run the main script:
```bash
python parse_auctions.py
```

---

## Лицензия / License
Этот проект распространяется под лицензией [MIT](https://opensource.org/licenses/MIT).

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). 