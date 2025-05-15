import os
import csv
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import sys
from dotenv import load_dotenv
from search_config.excluded_words import is_excluded
from search_config.quantity_extractor import extract_quantity
from search_config.status_extractor import extract_status
from settings.config import load_proxy_settings

# Загружаем переменные окружения
load_dotenv()


@dataclass
class AuctionItem:
    """
    Класс для хранения информации о лоте с Yahoo Auctions.
    Использует Python dataclass для автоматической генерации методов.

    Атрибуты:
        id (str): Уникальный идентификатор лота
        title (str): Название лота
        price (int): Текущая цена в йенах
        seller_id (str): ID продавца
        seller_name (str): Имя продавца
        end_time (str): Время окончания аукциона
        bids (int): Количество ставок
        url (str): Ссылка на лот
        image_url (str): Ссылка на изображение
        shipping_info (str): Информация о доставке
        quantity (int): Количество товара
        status (str): Статус товара
    """
    id: str
    title: str
    price: int
    seller_id: str
    seller_name: str
    end_time: str
    bids: int
    url: str
    image_url: str
    shipping_info: str
    quantity: int = 1
    status: str = ''


class YahooAuctionsParser:
    """
    Основной класс для парсинга Yahoo Auctions.

    Параметры:
        proxy (dict, optional): Настройки прокси в формате:
            {
                'http': 'http://user:pass@host:port',
                'https': 'https://user:pass@host:port'
            }
    """

    def __init__(self, proxy: Optional[dict] = None):
        self.proxy = proxy or {
            'http': os.getenv('PROXY_1'),
            'https': os.getenv('PROXY_2'),
            'socks5': os.getenv('PROXY_SOCKS5')
        }
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Создает и настраивает HTTP-сессию с заголовками и прокси."""
        session = requests.Session()

        if self.proxy:
            session.proxies.update(self.proxy)

        headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        }
        session.headers.update(headers)

        return session

    def search_items(self, query: str, page: int = 1, items_per_page: int = 50) -> List[AuctionItem]:
        """
        Поиск лотов по запросу с пагинацией.

        Параметры:
            query (str): Поисковый запрос
            page (int): Номер страницы (начинается с 1)
            items_per_page (int): Количество товаров на странице

        Возвращает:
            List[AuctionItem]: Список найденных лотов
        """
        url = self._build_search_url(query, page, items_per_page)
        print(f"Запрос страницы {page}: {url}")

        try:
            response = self._make_request(url)
            return self._parse_search_results(response.text)
        except Exception as e:
            print(f"Ошибка при поиске: {str(e)}")
            return []

    def _build_search_url(self, query: str, page: int, items_per_page: int) -> str:
        """Формирует URL для поиска с параметрами."""
        return (f"https://auctions.yahoo.co.jp/search/search"
                f"?p={query}"
                f"&b={(page-1)*items_per_page+1}"
                f"&n={items_per_page}")

    def _make_request(self, url: str) -> requests.Response:
        """Выполняет HTTP-запрос с обработкой ошибок."""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Сохранение HTML для отладки
        self._save_debug_html(response.text, url)
        return response

    def _save_debug_html(self, html: str, url: str) -> None:
        """Сохраняет HTML страницы в файл для отладки."""
        debug_dir = "debug_html"
        os.makedirs(debug_dir, exist_ok=True)

        filename = f"{debug_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<!-- {url} -->\n")
            f.write(html)
        print(f"Сохранено: {filename}")

    def _parse_search_results(self, html: str) -> List[AuctionItem]:
        """Парсит HTML страницы с результатами поиска."""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        for item in soup.select('div.Products__list li.Product'):
            try:
                auction_item = self._parse_item(item)
                if auction_item:
                    items.append(auction_item)
            except Exception as e:
                print(f"Ошибка парсинга: {str(e)}")
                continue

        return items

    def _parse_item(self, item) -> Optional[AuctionItem]:
        """Парсит отдельный элемент лота."""
        # Извлечение основных данных
        title_elem = item.select_one('a.Product__titleLink')
        if not title_elem:
            return None

        item_id = title_elem['href'].split('/')[-1]
        title = title_elem.text.strip()

        # Обработка исключений
        if is_excluded(title):
            return None

        # Извлечение дополнительных данных
        price = self._parse_price(item)
        seller = self._parse_seller(item)
        end_time = self._parse_end_time(item)
        bids = self._parse_bids(item)
        image_url = self._parse_image(item)
        shipping = self._parse_shipping(item)
        quantity = extract_quantity(title)
        status = extract_status(title)

        return AuctionItem(
            id=item_id,
            title=title,
            price=price,
            seller_id=seller['id'],
            seller_name=seller['name'],
            end_time=end_time,
            bids=bids,
            url=f"https://auctions.yahoo.co.jp/item/{item_id}",
            image_url=image_url,
            shipping_info=shipping,
            quantity=quantity,
            status=status
        )

    def _parse_price(self, item) -> int:
        """Извлекает цену из элемента."""
        price_elem = item.select_one('span.Product__priceValue')
        if price_elem:
            return int(price_elem.text.strip().replace('円', '').replace(',', ''))
        return 0

    def _parse_seller(self, item) -> dict:
        """Извлекает информацию о продавце."""
        seller_elem = item.select_one('span.Product__seller')
        return {
            'id': seller_elem.get('data-seller-id', ''),
            'name': seller_elem.text.strip() if seller_elem else ''
        }

    def _parse_end_time(self, item) -> str:
        """Извлекает время окончания аукциона."""
        time_elem = item.select_one('span.Product__time')
        return time_elem.text.strip() if time_elem else ''

    def _parse_bids(self, item) -> int:
        """Извлекает количество ставок."""
        bids_elem = item.select_one('span.Product__bid')
        if bids_elem:
            return int(bids_elem.text.strip().replace('入札', ''))
        return 0

    def _parse_image(self, item) -> str:
        """Извлекает URL изображения."""
        img_elem = item.select_one('img.Product__imageData')
        return img_elem.get('src', '') if img_elem else ''

    def _parse_shipping(self, item) -> str:
        """Извлекает информацию о доставке."""
        shipping_elem = item.select_one('span.Product__shipping')
        return shipping_elem.text.strip() if shipping_elem else ''


def save_items_to_csv(items: List[AuctionItem], filename: str) -> None:
    """
    Сохраняет список лотов в CSV файл.

    Параметры:
        items (List[AuctionItem]): Список лотов для сохранения
        filename (str): Имя файла (без пути)
    """
    if not items:
        print("Нет данных для сохранения")
        return

    os.makedirs('results', exist_ok=True)
    filepath = os.path.join('results', filename)

    fieldnames = list(AuctionItem.__annotations__.keys())

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item.__dict__)

    print(f"Сохранено {len(items)} лотов в {filepath}")


def main():
    """Основная функция"""
    # Создаем парсер
    parser = YahooAuctionsParser()

    # Получаем параметры поиска
    query = input("Введите поисковый запрос: ")
    pages = int(input("Введите количество страниц для поиска: "))

    all_items = []

    # Собираем товары со всех страниц
    for page in range(1, pages + 1):
        print(f"\nОбработка страницы {page} из {pages}")
        items = parser.search_items(query, page=page)
        all_items.extend(items)

        # Делаем паузу между запросами
        if page < pages:
            time.sleep(2)

    # Сохраняем результаты
    if all_items:
        filename = f"{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        save_items_to_csv(all_items, filename)

        # Выводим статистику
        print("\nСтатистика:")
        print(f"Всего найдено товаров: {len(all_items)}")
        print(
            f"Средняя цена: {sum(item.price for item in all_items) / len(all_items):,.0f}円")
        print(
            f"Минимальная цена: {min(item.price for item in all_items):,.0f}円")
        print(
            f"Максимальная цена: {max(item.price for item in all_items):,.0f}円")
        print(f"Всего ставок: {sum(item.bids for item in all_items)}")
    else:
        print("\nТовары не найдены")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Объединяем все аргументы через пробел
        filepath = ' '.join(sys.argv[1:])
        if not os.path.exists(filepath):
            print(f"Файл не найден: {filepath}")
            sys.exit(1)
    else:
        print("Укажите путь к CSV файлу в аргументах")
