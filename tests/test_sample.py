import json


def test_products_file_exists():
    with open('products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
