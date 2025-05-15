def extract_status(text: str) -> str:
    """
    Determines item condition status from Japanese description.

    :param text: Item description text
    :return: Status in English
    """
    status_map = {
        # New
        '新品': 'New',
        '未使用': 'Unused',
        '未開封': 'Sealed',

        # Used
        '中古': 'Used',
        '使用済': 'Used',
        '美品': 'Used (Excellent condition)',

        # For parts/not working
        'ジャンク': 'Junk/For parts',
        '訳あり': 'Defective/Junk',
        '故障': 'Broken',
        '破損': 'Damaged',
        '動作未確認': 'Untested',
        '動作しない': 'Not working',
        '不良品': 'Defective',
        '要修理': 'Needs repair',
        '部品取り': 'For parts',
        '外装のみ': 'Case only',
        '本体のみ': 'Device only (no accessories)',
        '電源入らず': "Won't power on",

        # Packaging
        '箱無し': 'No original box',
        '箱破損': 'Damaged box',
        '付属品なし': 'No accessories',

        # Bulk
        'まとめ売り': 'Bulk lot',
        '大量': 'Wholesale',
        '業者向け': 'For resellers',
        '卸売': 'Wholesale'
    }

    for jp_status, en_status in status_map.items():
        if jp_status in text:
            return en_status

    return ''  # If no status found
