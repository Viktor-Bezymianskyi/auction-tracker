import re

# Функция для извлечения количества товара из названия лота


def extract_quantity(text):
    """
    Извлекает количество товаров из текста, игнорируя цифры в кодах товаров.
    Возвращает 1, если количество не указано явно.
    """
    # Игнорируем цифры в кодах товаров (например, GPZ45RW, S2011-002-S)
    text = re.sub(r'[A-Za-z][A-Za-z0-9-]*\d{2,}[A-Za-z0-9-]*', '', text)

    # Преобразуем японские цифры в арабские
    jp_digits = str.maketrans({
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
    })
    text = text.translate(jp_digits)

    # Ищем только явные указания количества с единицами измерения
    patterns = re.findall(
        r'(?<!\d)(\d{1,2})\s*(個|台|点|本|枚|セット|pcs|units|口|unit|set|units|個セット|点セット)',
        text,
        flags=re.IGNORECASE
    )

    # Ищем указания на наборы (без конкретного числа)
    set_keywords = ['まとめ', '大量', 'ダブルパック', 'パック', 'セット', 'set', 'units']

    if patterns:
        return min(int(num) for num, unit in patterns)
    elif any(kw in text for kw in set_keywords):
        return 2  # если указано что это набор, но нет числа
    return 1  # по умолчанию


# Примеры для тестирования
if __name__ == "__main__":
    test_titles = [
        "PS Vita 本体 3台セット ジャンク",
        "DualSense x2 ワイヤレス",
        "PS4 CUH-1200 ×4",
        "Switch 本体 まとめ売り",
        "PS Vita 本体 PCH-2000ZA23",
        "64GB 2個 メモリーカード",
        "ZCT2J 15個 セット",
        "PS5 コントローラー パック",
    ]

    for title in test_titles:
        print(f"{title} → {extract_quantity(title)} 個")
