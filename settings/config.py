import os
from dotenv import load_dotenv

load_dotenv()

# Настройки прокси


def load_proxy_settings():
    return {
        'http': os.getenv('PROXY_1'),
        'https': os.getenv('PROXY_2'),
        'socks5': os.getenv('PROXY_SOCKS5')
    }


# Отладочные настройки
DEBUG_MODE = False
DEBUG_DIR = "debug_html"
