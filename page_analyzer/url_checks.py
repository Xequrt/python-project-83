import requests
from parser import parse


def check_url_availability(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.status_code
    except requests.RequestException:
        return None


def extract_metadata(url):
    return parse(url)


def run_all_checks(url_name):
    status_code = check_url_availability(url_name)
    metadata = extract_metadata(url_name)

    return {
        'status_code': status_code,
        'h1': metadata['h1'],
        'title': metadata['title'],
        'description': metadata['description']
    }
