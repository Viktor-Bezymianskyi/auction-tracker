import csv
from datetime import datetime
from yahoo_auctions_client import YahooAuctionsClient
import time
import os
import random
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re
import shutil
from dotenv import load_dotenv
from settings.config import load_proxy_settings, DEBUG_MODE, DEBUG_DIR

# Загружаем переменные из .env
load_dotenv()


# Получаем все User-Agent'ы из .env
USER_AGENTS = [
    os.getenv('USER_AGENT_1'),
    os.getenv('USER_AGENT_2'),
    os.getenv('USER_AGENT_3'),
    os.getenv('USER_AGENT_4'),
    os.getenv('USER_AGENT_5'),
]
current_user_agent_index = 0


def get_next_user_agent():
    """Получает следующий User-Agent из списка"""
    global current_user_agent_index
    user_agent = USER_AGENTS[current_user_agent_index]
    current_user_agent_index = (
        current_user_agent_index + 1) % len(USER_AGENTS)
    return user_agent


# === НАСТРОЙКИ ===
KEYWORDS = [
    "WH-1000XM4", "wf1000xm4", "wf1000xm5", "wh1000xm5", "Nintendo Switch",
    "ニンテンドースイッチアクセサリー(ニンテンドースイッチ テレビゲーム)",
    "DualSense", "「ps5コントローラー」(アクセサリ、周辺機器)",
    "amazon kindle 10",
    "Amazon Kindle", "電子ブックリーダー",
    "DualShock 4", "PS Vita本体", "ニンテンドー3DS本体(ニンテンドー3DS テレビゲーム)"
]


class ProxyManager:
    """Менеджер для работы с прокси"""

    def __init__(self):
        self.proxies = [
            {
                'http': os.getenv('PROXY_1'),
                'https': os.getenv('PROXY_1'),
                'socks5': os.getenv('PROXY_SOCKS5')
            },
            {
                'http': os.getenv('PROXY_2'),
                'https': os.getenv('PROXY_2'),
                'socks5': os.getenv('PROXY_SOCKS5')
            }
        ]
        self.current_proxy_index = 0

    def get_next_proxy(self) -> Dict:
        """Получение следующего прокси из списка"""
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (
            self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def get_random_proxy(self) -> Dict:
        """Получение случайного прокси из списка"""
        return random.choice(self.proxies)


def test_proxy(proxy: Dict) -> bool:
    global current_user_agent_index
    try:
        response = requests.get(
            'https://auctions.yahoo.co.jp',
            proxies=proxy,
            timeout=10,
            headers={
                'User-Agent': USER_AGENTS[current_user_agent_index],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка при проверке прокси {proxy['http'].split('@')[1]}: {e}")
        # Меняем User-Agent при ошибке
        current_user_agent_index = (
            current_user_agent_index + 1) % len(USER_AGENTS)
        return False


def analyze_html(html: str) -> None:
    """
    Анализ HTML страницы для отладки (работает только в DEBUG_MODE)
    :param html: HTML страница
    """
    if not DEBUG_MODE:
        return

    os.makedirs(DEBUG_DIR, exist_ok=True)

    # Сохраняем полный HTML
    debug_filename = os.path.join(
        DEBUG_DIR, f"debug_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(debug_filename, 'w', encoding='utf-8') as f:
        f.write(html)

    # Сохраняем структуру
    soup = BeautifulSoup(html, 'html.parser')
    structure_filename = os.path.join(
        DEBUG_DIR, f"html_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(structure_filename, 'w', encoding='utf-8') as f:
        f.write("Структура HTML:\n")
        for tag in soup.find_all(['div', 'section', 'ul', 'li']):
            if tag.get('class'):
                f.write(f"<{tag.name} class='{' '.join(tag['class'])}'>\n")

    print(f"\nОтладочные файлы сохранены в: {DEBUG_DIR}")


def save_items_to_csv(items, filename):
    """
    Сохранение информации о лотах в CSV файл

    :param items: Список лотов (dict)
    :param filename: Имя файла для сохранения
    """
    os.makedirs('results', exist_ok=True)
    filepath = os.path.join('results', filename)

    fieldnames = [
        'Название лота',
        'Цена (¥)',
        'Ссылка',
        'Кол-во ставок',
        'Окончание',
        'Дата добавления',
        'Продавец',
        'ID лота',
        'Прокси'
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            writer.writerow({
                'Название лота': item.get('title', ''),
                'Цена (¥)': item.get('price', 0),
                'Ссылка': item.get('url', ''),
                'Кол-во ставок': item.get('bids', 0),
                'Окончание': item.get('end_time', ''),
                'Дата добавления': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Продавец': item.get('seller_name', ''),
                'ID лота': item.get('id', ''),
                'Прокси': item.get('proxy_used', '')
            })


def extract_items_from_html(html):
    """
    Извлекает лоты из HTML страницы поиска Yahoo Auctions
    :param html: HTML страницы
    :return: список объектов с нужными полями
    """
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    products_list = soup.find('div', class_='Products__list')

    if not products_list:
        print("Не найдено списка товаров на странице")
        return items

    for item in products_list.find_all('li', class_='Product'):
        try:
            title_link = item.find('a', class_='Product__titleLink')
            if not title_link:
                continue

            end_time_elem = item.find('span', class_='Product__time')
            end_time = end_time_elem.text.strip() if end_time_elem else ''

            lot_id = title_link['href'].split('/')[-1]
            title = title_link.text.strip()

            price_elem = item.find('span', class_='Product__priceValue')
            price = int(price_elem.text.strip().replace(
                '円', '').replace(',', '')) if price_elem else 0

            bids_elem = item.find('span', class_='Product__bid')
            bids = int(bids_elem.text.strip().replace(
                '入札', '')) if bids_elem else 0

            seller_elem = item.find('span', class_='Product__seller')
            seller_name = seller_elem.text.strip() if seller_elem else ''

            url = title_link['href']

            items.append({
                'id': lot_id,
                'title': title,
                'price': price,
                'bids': bids,
                'seller_name': seller_name,
                'url': url,
                'end_time': end_time  # Добавляем время окончания
            })

        except Exception as e:
            print(f"Ошибка парсинга лота: {e}")
            continue

    return items


def convert_to_zenmarket_url(yahoo_url):
    # Извлекаем itemCode из ссылки Yahoo
    m = re.search(r'/auction/([a-zA-Z0-9]+)', yahoo_url)
    if m:
        item_code = m.group(1)
        return f'https://zenmarket.jp/ru/auction.aspx?itemCode={item_code}'
    return yahoo_url


def is_ending_soon(end_time_str: str) -> bool:
    """
    Проверяет, заканчивается ли лот в течение 1 дня или меньше.
    Поддерживает форматы: '3日', '19時間', '1日', '12時間', '59分'

    :param end_time_str: Строка с временем окончания на японском
    :return: True если до окончания <= 1 дня, иначе False
    """
    if not end_time_str:
        return False

    try:
        if '日' in end_time_str:  # Пример: "1日" (1 день)
            days = int(re.search(r'(\d+)日', end_time_str).group(1))
            return days <= 1  # 1 день или меньше

        elif '時間' in end_time_str:  # Пример: "12時間" (12 часов)
            hours = int(re.search(r'(\d+)時間', end_time_str).group(1))
            return hours <= 24  # Меньше суток

        elif '分' in end_time_str:  # Пример: "59分" (59 минут)
            return True  # Любое количество минут - считаем "скоро"

    except Exception as e:
        print(f"Ошибка парсинга времени окончания '{end_time_str}': {e}")

    return False


def get_search_url(search_query, page, sort='end', order='a', filters=None):
    """
    Генерирует URL для поиска на Yahoo Auctions с сортировкой

    :param search_query: Поисковый запрос
    :param page: Номер страницы (начинается с 1)
    :param sort: Поле для сортировки:
        'end' - по времени окончания (по умолчанию)
        'cbids' - по текущей цене
        'bidorbuy' - по цене "купить сейчас"
        'acc' - по времени добавления
        'bids' - по количеству ставок
    :param order: Порядок сортировки:
        'a' - по возрастанию (ascending, по умолчанию)
        'd' - по убыванию (descending)
    :param filters: Дополнительные фильтры (dict):
        'min_price': минимальная цена
        'max_price': максимальная цена
        'condition': состояние товара
        'shipping': варианты доставки
    :return: Сформированный URL для запроса

    Примеры использования:
    1. Сортировка по времени окончания (скоро заканчивающиеся первыми):
       get_search_url("kindle", 1, sort='end', order='a')

    2. Сортировка по цене (от дешевых к дорогим):
       get_search_url("kindle", 1, sort='cbids', order='a')

    3. Сортировка по количеству ставок (много ставок сначала):
       get_search_url("kindle", 1, sort='bids', order='d')
    """
    base_url = "https://auctions.yahoo.co.jp/search/search"
    params = {
        'p': search_query,
        'b': (page-1)*50+1,
        'n': 50,
        's1': sort,  # Поле сортировки
        'o1': order  # Порядок сортировки
    }

    if filters:
        if 'min_price' in filters:
            params['va'] = filters['min_price']
        if 'max_price' in filters:
            params['ve'] = filters['max_price']
        if 'condition' in filters:
            params['cond'] = filters['condition']
        if 'shipping' in filters:
            params['ship'] = filters['shipping']

    return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"


def main():
    proxy_manager = ProxyManager()

    print("Проверка прокси...")
    working_proxies = [p for p in proxy_manager.proxies if test_proxy(p)]

    if not working_proxies:
        print("Нет работающих прокси. Проверьте настройки и доступность серверов.")
        return

    proxy_manager.proxies = working_proxies

    if DEBUG_MODE and os.path.exists(DEBUG_DIR):
        shutil.rmtree(DEBUG_DIR)

    for search_query in KEYWORDS:
        print(f"\n=== Поиск по ключу: {search_query} ===")
        all_items = []
        page = 1

        while True:
            print(f"\nПолучение страницы {page}...")
            proxy = proxy_manager.get_random_proxy()
            print(f"Используется прокси: {proxy['http'].split('@')[1]}")

            try:
                client = YahooAuctionsClient(proxy=proxy)
                search_url = get_search_url(
                    search_query,
                    page,
                    sort='end',
                    order='a'
                )
                print(f"URL запроса: {search_url}")

                response = client.session.get(search_url)
                response.raise_for_status()

                if DEBUG_MODE:
                    analyze_html(response.text)

                items = extract_items_from_html(response.text)
                if not items:
                    print(f"На странице {page} лоты не найдены")
                    break

                for item in items:
                    item['proxy_used'] = proxy['http'].split('@')[1]

                print(f"Найдено {len(items)} лотов")
                all_items.extend(items)
                page += 1
                time.sleep(1)

            except Exception as e:
                print(f"Ошибка при получении страницы {page}: {e}")
                break

        if all_items:
            # Создаем имя файла на основе поискового запроса
            # Заменяем спецсимволы и ограничиваем длину
            query_clean = re.sub(r'[^\w]', '_', search_query)[:20]
            filename = f"{query_clean}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            save_items_to_csv(all_items, filename)
            print(f"\nВсего найдено лотов: {len(all_items)}")
            print(f"Результаты сохранены в файл: {filename}")
        else:
            print("Лоты не найдены")


__all__ = [
    'convert_to_zenmarket_url',
    'save_items_to_csv'
]

if __name__ == "__main__":
    main()
