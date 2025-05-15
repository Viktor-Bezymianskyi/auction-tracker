import csv
from datetime import datetime
from googletrans import Translator
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from parse_auctions import convert_to_zenmarket_url
import re
import os
import argparse
import time
import shutil
from search_config.quantity_extractor import extract_quantity
from search_config.status_extractor import extract_status
from search_config.excluded_words import is_excluded
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настройки (теперь берутся из .env)
CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
YEN_TO_EUR = float(os.getenv('YEN_TO_EUR', '165'))
RESULTS_DIR = "results"
ARCHIVE_DIR = "results_archive"


def create_new_spreadsheet():
    """Создает новую таблицу с текущей датой"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope)
    gc = gspread.authorize(creds)

    # Формируем имя таблицы
    spreadsheet_name = f"yahoo_{datetime.now().strftime('%Y%m%d_%H%M')}"

    try:
        spreadsheet = gc.create(spreadsheet_name)
        # Даем доступ вашему email (замените на ваш)
        spreadsheet.share(os.getenv('GOOGLE_SHEETS_EMAIL'),
                          perm_type='user', role='writer')
        print(f"Создана новая таблица: {spreadsheet_name}")
        return spreadsheet
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")
        raise


def archive_file(filepath):
    """Перемещает файл в архивную папку"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    try:
        shutil.move(filepath, os.path.join(
            ARCHIVE_DIR, os.path.basename(filepath)))
        print(f"Файл перемещен в архив: {ARCHIVE_DIR}")
    except Exception as e:
        print(f"Ошибка при архивировании файла: {e}")


def process_all_results(date_override=None):
    """Обрабатывает все CSV файлы из папки results"""
    if not os.path.exists(RESULTS_DIR):
        print(f"Папка {RESULTS_DIR} не найдена")
        return

    try:
        # Создаем новую таблицу
        spreadsheet = create_new_spreadsheet()
        time.sleep(5)  # Даем время на создание таблицы
    except Exception:
        return

    # Авторизация Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope)
    gc = gspread.authorize(creds)

    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('.csv'):
            filepath = os.path.join(RESULTS_DIR, filename)
            print(f"\nОбработка файла: {filename}")

            # Определяем имя листа (убираем дату и ограничиваем длину)
            sheet_name = re.sub(r'_\d{8}_\d{4}\.csv$', '', filename)[:100]

            try:
                # Создаем новый лист
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows="1000", cols="20")
                time.sleep(2)

                # Подготавливаем данные
                translator = Translator()
                batch_data = []

                with open(filepath, mode='r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            title = row['Название лота']
                            if is_excluded(title):
                                continue

                            qty = extract_quantity(title)
                            status = extract_status(title)

                            try:
                                title_ru = translator.translate(
                                    title, src='ja', dest='ru').text
                            except Exception as e:
                                print(f"Ошибка перевода: {e}")
                                title_ru = title

                            add_date = date_override if date_override else datetime.now().strftime('%Y-%m-%d %H:%M')

                            batch_data.append([
                                title_ru or '',
                                round(int(row['Цена (¥)']) / YEN_TO_EUR, 2),
                                qty,
                                convert_to_zenmarket_url(row['Ссылка']),
                                row['Окончание'],
                                add_date,
                                status or '',
                                row['Цена (¥)']
                            ])
                        except Exception as e:
                            print(f"Ошибка при обработке строки: {e}")
                            continue

                # Записываем заголовки
                headers = [
                    'Название', 'Цена (EUR)', 'Количество', 'URL',
                    'Время окончания', 'Дата добавления', 'Статус', 'Цена (JPY)'
                ]
                worksheet.append_row(headers)
                time.sleep(1)

                # Пакетная вставка данных
                batch_size = 100
                for i in range(0, len(batch_data), batch_size):
                    chunk = batch_data[i:i + batch_size]
                    worksheet.append_rows(chunk)
                    print(f"Добавлено {len(chunk)} строк...")
                    time.sleep(2)

                print(
                    f"Файл {filename} успешно обработан. Всего добавлено {len(batch_data)} строк.")

                # Архивируем файл после успешной обработки
                archive_file(filepath)

            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {str(e)}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Обработка CSV файлов с аукционов')
    parser.add_argument(
        '--date', help='Дата в формате ГГГГ-ММ-ДД для переопределения даты добавления')

    args = parser.parse_args()

    # Преобразуем дату если она указана
    date_override = None
    if args.date:
        try:
            date_override = datetime.strptime(
                args.date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            print("Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
            exit(1)

    # Обработка всех файлов в папке results
    process_all_results(date_override=date_override)
