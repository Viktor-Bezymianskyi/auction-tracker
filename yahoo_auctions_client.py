import requests
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re


@dataclass
class SearchParams:
    """Параметры поиска на Yahoo Auctions"""
    query: str
    page: int = 1
    sort: str = "newest"  # newest, price_asc, price_desc, bids
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[str] = None  # new, used
    shipping: Optional[str] = None  # free, paid
    # True - только магазины, False - только частные продавцы
    store: Optional[bool] = None


@dataclass
class AuctionItem:
    """Класс для хранения информации о лоте"""
    id: str
    title: str
    price: float
    seller_id: str
    seller_name: str
    end_time: datetime
    bids: int
    url: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    shipping_info: Optional[Dict] = None


class YahooAuctionsClient:
    """Клиент для работы с API Yahoo Auctions"""

    BASE_URL = "https://auctions.yahoo.co.jp"
    API_BASE_URL = f"{BASE_URL}/api"

    def __init__(self, proxy: Optional[Dict] = None):
        """
        Инициализация клиента

        :param proxy: Словарь с настройками прокси (например, {'http': 'http://user:pass@host:port'})
        """
        self.session = requests.Session()
        if proxy:
            self.session.proxies.update(proxy)

        # Базовые заголовки
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.BASE_URL,
        })

    def _parse_search_results(self, html: str) -> List[AuctionItem]:
        """Парсинг результатов поиска"""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        # Находим все карточки товаров
        products_list = soup.find('div', class_='Products__list')
        product_cards = products_list.find_all(
            'li', class_='Product') if products_list else []

        for card in product_cards:
            try:
                # Получаем ID лота из ссылки
                link = card.select_one('a.Product__titleLink')
                if not link:
                    continue

                item_id = re.search(
                    r'/jp/auction/([^/]+)', link['href']).group(1)

                # Получаем заголовок
                title = link.text.strip()

                # Получаем цену
                price_elem = card.select_one('span.Product__priceValue')
                price = float(price_elem.text.strip().replace(
                    '円', '').replace(',', '')) if price_elem else 0.0

                # Получаем информацию о продавце
                seller_elem = card.select_one('span.Product__seller')
                seller_name = seller_elem.text.strip() if seller_elem else ''
                seller_id = seller_elem['data-userid'] if seller_elem and 'data-userid' in seller_elem.attrs else ''

                # Получаем время окончания
                end_time_elem = card.select_one('span.Product__time')
                end_time = datetime.strptime(end_time_elem.text.strip(
                ), '%Y/%m/%d %H:%M') if end_time_elem else datetime.now()

                # Получаем количество ставок
                bids_elem = card.select_one('span.Product__bid')
                bids = int(re.search(r'\d+', bids_elem.text).group()
                           ) if bids_elem else 0

                # Получаем URL изображения
                img_elem = card.select_one('img.Product__imageData')
                image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None

                items.append(AuctionItem(
                    id=item_id,
                    title=title,
                    price=price,
                    seller_id=seller_id,
                    seller_name=seller_name,
                    end_time=end_time,
                    bids=bids,
                    url=f"{self.BASE_URL}/jp/auction/{item_id}",
                    image_url=image_url
                ))

            except Exception as e:
                print(f"Ошибка при парсинге карточки товара: {e}")
                continue

        return items

    def _parse_item_details(self, html: str, shipping_info: Dict) -> AuctionItem:
        """Парсинг детальной информации о лоте"""
        soup = BeautifulSoup(html, 'html.parser')

        # Получаем ID лота из URL
        item_id = re.search(r'/jp/auction/([^/]+)', html).group(1)

        # Получаем заголовок
        title = soup.select_one('h1.ProductTitle__text').text.strip()

        # Получаем цену
        price_elem = soup.select_one('span.ProductInformation__price')
        price = float(price_elem.text.strip().replace(
            '円', '').replace(',', '')) if price_elem else 0.0

        # Получаем информацию о продавце
        seller_elem = soup.select_one('div.Seller__name')
        seller_name = seller_elem.text.strip() if seller_elem else ''
        seller_id = seller_elem['data-userid'] if seller_elem and 'data-userid' in seller_elem.attrs else ''

        # Получаем время окончания
        end_time_elem = soup.select_one('span.ProductInformation__time')
        end_time = datetime.strptime(end_time_elem.text.strip(
        ), '%Y/%m/%d %H:%M') if end_time_elem else datetime.now()

        # Получаем количество ставок
        bids_elem = soup.select_one('span.ProductInformation__bid')
        bids = int(re.search(r'\d+', bids_elem.text).group()
                   ) if bids_elem else 0

        # Получаем описание
        description_elem = soup.select_one('div.ProductDescription__text')
        description = description_elem.text.strip() if description_elem else None

        # Получаем категорию
        category_elem = soup.select_one('div.ProductCategory__name')
        category = category_elem.text.strip() if category_elem else None

        # Получаем URL изображения
        img_elem = soup.select_one('img.ProductImage__main')
        image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None

        return AuctionItem(
            id=item_id,
            title=title,
            price=price,
            seller_id=seller_id,
            seller_name=seller_name,
            end_time=end_time,
            bids=bids,
            url=f"{self.BASE_URL}/jp/auction/{item_id}",
            image_url=image_url,
            description=description,
            category=category,
            shipping_info=shipping_info
        )

    def search_items(self,
                     query: str,
                     page: int = 1,
                     items_per_page: int = 50,
                     category: Optional[str] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     sort: str = 'end') -> List[AuctionItem]:
        """
        Поиск лотов

        :param query: Поисковый запрос
        :param page: Номер страницы
        :param items_per_page: Количество товаров на странице
        :param category: ID категории
        :param min_price: Минимальная цена
        :param max_price: Максимальная цена
        :param sort: Сортировка (end - по времени окончания, bid - по количеству ставок, price - по цене)
        :return: Список найденных лотов
        """
        params = {
            'p': query,
            'va': query,
            'b': (page - 1) * items_per_page + 1,
            'n': items_per_page,
            'is_postage_mode': 1,
            'dest_pref_code': 13,  # Токио
        }

        if category:
            params['auccat'] = category
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        if sort:
            params['s1'] = sort

        response = self.session.get(
            f"{self.BASE_URL}/search/search", params=params)
        response.raise_for_status()

        return self._parse_search_results(response.text)

    def get_item_details(self, item_id: str) -> AuctionItem:
        """
        Получение детальной информации о лоте

        :param item_id: ID лота
        :return: Информация о лоте
        """
        # Получаем основную информацию о лоте
        response = self.session.get(f"{self.BASE_URL}/jp/auction/{item_id}")
        response.raise_for_status()

        # Получаем информацию о доставке
        shipping_response = self.session.get(
            f"{self.BASE_URL}/web/api/itempage/v1/shipments/auction/items/{item_id}",
            params={'aid': item_id, 'prefCode': 13}
        )
        shipping_response.raise_for_status()

        return self._parse_item_details(response.text, shipping_response.json())

    def get_seller_items(self, seller_id: str, exclude_item_id: Optional[str] = None) -> List[AuctionItem]:
        """
        Получение списка лотов продавца

        :param seller_id: ID продавца
        :param exclude_item_id: ID лота, который нужно исключить из результатов
        :return: Список лотов продавца
        """
        params = {'aucUserId': seller_id}
        if exclude_item_id:
            params['exceptAuctionId'] = exclude_item_id

        response = self.session.get(
            f"{self.BASE_URL}/web/api/itempage/v2/search/featuredSearch",
            params=params
        )
        response.raise_for_status()

        data = response.json()
        items = []

        for item_data in data.get('items', []):
            try:
                items.append(AuctionItem(
                    id=item_data['auctionId'],
                    title=item_data['title'],
                    price=float(item_data['price']),
                    seller_id=seller_id,
                    seller_name=item_data.get('sellerName', ''),
                    end_time=datetime.fromtimestamp(item_data['endTime']),
                    bids=int(item_data.get('bids', 0)),
                    url=f"{self.BASE_URL}/jp/auction/{item_data['auctionId']}",
                    image_url=item_data.get('imageUrl')
                ))
            except Exception as e:
                print(f"Ошибка при парсинге лота продавца: {e}")
                continue

        return items

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Получение поисковых подсказок

        :param query: Поисковый запрос
        :param limit: Максимальное количество подсказок
        :return: Список подсказок
        """
        response = self.session.get(
            f"{self.API_BASE_URL}/search/v1/suggest/queries",
            params={'query': query, 'limit': limit, 'categoryLimit': 5}
        )
        response.raise_for_status()

        data = response.json()
        return [suggestion['query'] for suggestion in data.get('suggestions', [])]


# Пример использования
if __name__ == "__main__":
    # Настройка прокси
    proxy = {
        'http': 'http://photoprint10x20:SWasJFs9Q9@45.80.48.117:50100',
        'https': 'http://photoprint10x20:SWasJFs9Q9@45.80.48.117:50100'
    }

    # Создание клиента
    client = YahooAuctionsClient(proxy=proxy)

    # Поиск лотов
    items = client.search_items("dualsense", page=1, items_per_page=50)
    print(f"Найдено лотов: {len(items)}")

    # Вывод информации о найденных лотах
    for item in items:
        print(f"\nЛот: {item.title}")
        print(f"Цена: {item.price}円")
        print(f"Продавец: {item.seller_name}")
        print(f"Ставок: {item.bids}")
        print(f"Окончание: {item.end_time}")
        print(f"URL: {item.url}")

    # Получение деталей первого лота
    if items:
        item_details = client.get_item_details(items[0].id)
        print(f"\nДетали лота:")
        print(f"Заголовок: {item_details.title}")
        print(f"Цена: {item_details.price}円")
        print(f"Продавец: {item_details.seller_name}")
        print(f"Ставок: {item_details.bids}")
        print(f"Окончание: {item_details.end_time}")
        print(f"Категория: {item_details.category}")
        print(f"Описание: {item_details.description[:200]}...")
        print(f"Информация о доставке: {item_details.shipping_info}")

    # Получение поисковых подсказок
    suggestions = client.get_search_suggestions("dualsense")
    print(f"\nПоисковые подсказки: {suggestions}")
