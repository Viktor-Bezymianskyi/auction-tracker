#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Yahoo Auctions API Monitor / Монитор API Yahoo Auctions
=======================================================

A tool to intercept and analyze Yahoo Auctions Japan API traffic through mitmproxy.
Инструмент для перехвата и анализа API-трафика Yahoo Auctions Japan через mitmproxy.

Features / Возможности:
- Intercepts all HTTP requests to Yahoo Auctions / Перехват всех HTTP-запросов к Yahoo Auctions
- Identifies API requests by URL and headers / Идентифицирует API-запросы по URL и заголовкам
- Logs requests and responses to JSON files / Логирует запросы и ответы в JSON-файлы
- Collects API endpoint statistics / Собирает статистику по API-эндпоинтам

Usage / Использование:
1. Run mitmproxy with this script: / Запустите mitmproxy с этим скриптом:
   mitmproxy -s yahoo_auctions_api.py
   
2. Alternative with log saving: / Альтернатива с сохранением лога:
   mitmdump -s yahoo_auctions_api.py -w traffic.log
   
3. Configure your device/browser to use mitmproxy as proxy
   Настройте устройство/браузер на использование mitmproxy в качестве прокси
"""

import mitmproxy.http
from mitmproxy import ctx
import json
import re
from datetime import datetime
import os


class YahooAuctionsAPI:
    """
    Main class for intercepting and analyzing Yahoo Auctions API traffic
    Основной класс для перехвата и анализа API-трафика Yahoo Auctions

    Attributes / Атрибуты:
        api_endpoints (set): Set of unique API endpoints / Множество уникальных API-эндпоинтов
        log_dir (str): Directory for log files / Директория для логов
        request_count (int): Total request counter / Счетчик всех запросов
        api_request_count (int): API request counter / Счетчик API-запросов
    """

    def __init__(self):
        """Initialize with default values / Инициализация с значениями по умолчанию"""
        self.api_endpoints = set()
        self.log_dir = "yahoo_api_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.request_count = 0
        self.api_request_count = 0

    def _is_api_request(self, flow: mitmproxy.http.HTTPFlow) -> bool:
        """
        Check if request is Yahoo Auctions API request
        Проверяет, является ли запрос API-запросом Yahoo Auctions

        Args / Параметры:
            flow: mitmproxy HTTP flow object / Объект HTTP-потока mitmproxy

        Returns / Возвращает:
            bool: True if API request / True если API-запрос
        """
        path = flow.request.path
        headers = flow.request.headers
        host = flow.request.pretty_host

        # Проверяем только запросы к Yahoo Auctions
        is_api = (
            'auctions.yahoo.co.jp' in host and
            (
                '/api/' in path or
                '/json/' in path or
                path.endswith('.json') or
                'application/json' in headers.get('accept', '').lower() or
                'application/json' in headers.get('content-type', '').lower() or
                '/search/' in path or
                '/item/' in path or
                '/category/' in path or
                '/user/' in path or
                '/bid/' in path or
                '/auction/' in path or
                '/v1/' in path or
                '/v2/' in path or
                '/graphql' in path or
                '/rest/' in path or
                'xhr' in path.lower() or
                'ajax' in path.lower() or
                'data' in path.lower() or
                'query' in path.lower() or
                'jlp' in path.lower() or  # Yahoo Japan API часто использует префикс jlp
                'auction' in path.lower() or
                'item' in path.lower() or
                'search' in path.lower() or
                'category' in path.lower() or
                'user' in path.lower() or
                'bid' in path.lower() or
                'price' in path.lower() or
                'status' in path.lower() or
                'info' in path.lower()
            )
        )

        # Логируем все запросы к Yahoo Auctions для анализа
        if 'auctions.yahoo.co.jp' in host:
            ctx.log.info(
                f"Проверка запроса к Yahoo Auctions: {flow.request.method} {flow.request.pretty_url}")
            ctx.log.info(f"Host: {host}")
            ctx.log.info(f"Path: {path}")
            ctx.log.info(f"Headers: {dict(headers)}")

            if is_api:
                ctx.log.info(
                    f"Найден API запрос к Yahoo Auctions: {flow.request.method} {flow.request.pretty_url}")
                ctx.log.info(f"Headers: {dict(headers)}")

        return is_api

    def _save_to_file(self, data, prefix):
        """
        Save data to JSON file with timestamp
        Сохраняет данные в JSON-файл с временной меткой

        Args / Параметры:
            data: Data to save / Данные для сохранения
            prefix: Filename prefix / Префикс имени файла

        Returns / Возвращает:
            str: Path to saved file / Путь к сохраненному файлу
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_dir}/{prefix}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename

    def request(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        Process outgoing HTTP requests
        Обрабатывает исходящие HTTP-запросы
        """
        # Логируем только запросы к Yahoo Auctions
        if 'auctions.yahoo.co.jp' in flow.request.pretty_host:
            self.request_count += 1

            request_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "headers": dict(flow.request.headers),
                "cookies": dict(flow.request.cookies.fields)
            }

            if flow.request.content:
                try:
                    body = json.loads(flow.request.content)
                    request_data["body"] = body
                except:
                    request_data["body"] = flow.request.content.decode(
                        'utf-8', errors='ignore')

            filename = self._save_to_file(request_data, "all_requests")
            ctx.log.info(
                f"Запрос #{self.request_count} к Yahoo Auctions: {flow.request.method} {flow.request.pretty_url} -> {filename}")

            if self._is_api_request(flow):
                self.api_request_count += 1
                endpoint = f"{flow.request.method} {flow.request.path}"
                self.api_endpoints.add(endpoint)
                filename = self._save_to_file(request_data, "api_request")
                ctx.log.info(
                    f"API Request #{self.api_request_count} к Yahoo Auctions: {endpoint} -> {filename}")

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        Process incoming HTTP responses
        Обрабатывает входящие HTTP-ответы
        """
        if self._is_api_request(flow):
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "cookies": dict(flow.response.cookies.fields)
            }

            if flow.response.content:
                try:
                    body = json.loads(flow.response.content)
                    response_data["body"] = body
                except:
                    response_data["body"] = flow.response.content.decode(
                        'utf-8', errors='ignore')

            filename = self._save_to_file(response_data, "api_response")
            ctx.log.info(
                f"API Response от Yahoo Auctions: {flow.request.method} {flow.request.path} -> {filename}")

    def done(self):
        """
        Called when mitmproxy finishes
        Вызывается при завершении работы mitmproxy

        Saves collected statistics to file:
        Сохраняет собранную статистику в файл:
        - Total requests / Всего запросов
        - API requests / API-запросов
        - Unique endpoints / Уникальных эндпоинтов
        """
        # Сохраняем статистику и все найденные эндпоинты
        stats = {
            "total_requests": self.request_count,
            "api_requests": self.api_request_count,
            "endpoints": sorted(list(self.api_endpoints))
        }

        stats_file = f"{self.log_dir}/stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        ctx.log.info(f"Статистика сохранена в {stats_file}")
        ctx.log.info(f"Всего запросов к Yahoo Auctions: {self.request_count}")
        ctx.log.info(
            f"API запросов к Yahoo Auctions: {self.api_request_count}")
        ctx.log.info(
            f"Уникальных эндпоинтов Yahoo Auctions: {len(self.api_endpoints)}")


# Mitmproxy addon registration / Регистрация аддона в mitmproxy
addons = [
    YahooAuctionsAPI()
]

"""
Additional Notes / Дополнительные заметки:
-----------------------------------------
1. For proper SSL interception, install mitmproxy CA certificate:
   Для корректного перехвата SSL установите сертификат CA mitmproxy:
   - http://mitm.it

2. To monitor mobile devices / Для мониторинга мобильных устройств:
   - Configure proxy settings on device / Настройте прокси на устройстве
   - Install CA certificate / Установите CA сертификат
   - Typical proxy: <your-PC-IP>:8080 / Типичный прокси: <IP-вашего-ПК>:8080

3. Log files structure / Структура лог-файлов:
   - all_requests_*.json - All requests / Все запросы
   - api_request_*.json - API requests / API-запросы  
   - api_response_*.json - API responses / API-ответы
   - stats_*.json - Session statistics / Статистика сессии
"""
