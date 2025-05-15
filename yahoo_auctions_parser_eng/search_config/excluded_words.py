import re


def is_excluded(text: str) -> bool:
    """
    Check if item should be excluded based on Japanese description.
    Returns True if item contains exclusion keywords.
    """
    exclude_keywords = [
        # Accessories and parts (Japanese)
        'バッテリー', '充電器', '電池', 'カバー', 'フィルム',
        '保護フィルム', 'シート', 'ケース', 'カバー', 'アクセサリー',
        '交換用', 'パーツ', '部品', '修理用', '補修品',

        # Clarifications that it's just an accessory/part
        'のみ', 'だけ', '専用', '付属品', '附属品', 'オプション',

        # Books and manuals
        'マニュアル', '指南', '解説', '方法', 'ガイド', '本',
        '書籍', '出版', 'Kindle本', '電子書籍',

        # Specific exclusion phrases
        '箱のみ', '説明書のみ', '充電器のみ', 'ケースのみ',
        'カバーのみ', 'フィルムのみ', '付属品のみ',
        '保護フィルムとガラス', '充電器、ケースのみ',

        # Repair and parts
        '修理', 'ジャンク', '故障', '分解', '再生品',
        '中古品', '再生部品', '修理キット',

        # Certificates and compatibility
        'PSE認証', '適合品', '互換品', '汎用', '互換',
    ]

    # Additional checks for complex cases
    exclusion_patterns = [
        r'【.+のみ】',  # Patterns like 【充電器のみ】
        r'^[Ａ-Ｚa-z0-9-]+$',  # Only product codes
        r'[0-9]{4}-[0-9]{3}',  # Codes like 1234-567
    ]

    # Check keywords
    if any(kw in text for kw in exclude_keywords):
        return True

    # Check regex patterns
    if any(re.search(pattern, text) for pattern in exclusion_patterns):
        return True

    return False
