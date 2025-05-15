import re


def extract_quantity(text: str) -> int:
    """
    Extracts product quantity from Japanese text, ignoring numbers in product codes.
    Returns 1 if quantity is not explicitly specified.
    """
    # Remove product codes (e.g. GPZ45RW, S2011-002-S)
    text = re.sub(r'[A-Za-z][A-Za-z0-9-]*\d{2,}[A-Za-z0-9-]*', '', text)

    # Convert Japanese numerals to Arabic
    jp_digits = str.maketrans({
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
    })
    text = text.translate(jp_digits)

    # Find explicit quantity indications
    patterns = re.findall(
        r'(?<!\d)(\d{1,2})\s*(個|台|点|本|枚|セット|pcs|units|口|unit|set|units|個セット|点セット)',
        text,
        flags=re.IGNORECASE
    )

    # Check for set keywords
    set_keywords = ['まとめ', '大量', 'ダブルパック', 'パック', 'セット', 'set', 'units']

    if patterns:
        return min(int(num) for num, unit in patterns)
    elif any(kw in text for kw in set_keywords):
        return 2  # Default for sets without quantity
    return 1  # Default single item
