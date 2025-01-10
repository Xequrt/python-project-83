import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)


def parse(url):
    try:
        result = requests.get(url=url)
        result.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")
        return {
            'h1': '',
            'title': '',
            'description': ''
        }

    soup = BeautifulSoup(result.text, 'lxml')
    result_dict = {
        'h1': '',
        'title': '',
        'description': ''
    }

    h1_view = soup.find('h1')
    title_view = soup.find('title')
    description_view = soup.find('meta', {'name': 'description'})

    if h1_view:
        result_dict['h1'] = h1_view.get_text()
    if title_view:
        result_dict['title'] = title_view.get_text()
    if description_view:
        result_dict['description'] = description_view.get('content')
    return result_dict
