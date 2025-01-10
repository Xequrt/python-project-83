from flask import Flask, render_template, request, redirect, url_for, flash
from urllib.parse import urlparse
from page_analyzer.db_operations import (get_url_by_name, insert_url,
                           get_url_name_by_id, get_all_urls, get_url_checks)
from page_analyzer.validators_url import is_valid_url, is_len_valid
from page_analyzer.checks import run_check
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key')


@app.route('/')
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']
    parsed_url = urlparse(url)
    normalized_url = parsed_url.geturl()

    if not is_valid_url(normalized_url) or not is_len_valid(normalized_url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index'))

    existing_url = get_url_by_name(normalized_url)

    if existing_url:
        flash('Страница уже существует', 'info')
        url_id = existing_url[0]

    else:
        url_id = insert_url(normalized_url)
        flash('Страница успешно добавлена!', 'success')

    return redirect(url_for('url_detail', url_id=url_id))


@app.route('/urls')
def urls():
    urls_list = get_all_urls()
    return render_template('urls.html', urls=urls_list)


@app.route('/urls/<int:url_id>')
def url_detail(url_id):
    url_entry = get_url_name_by_id(url_id)
    if url_entry is None:
        return "URL not found", 404

    checks = get_url_checks(url_id)
    url_data = {
        'id': url_entry[0],
        'name': url_entry[1],
        'created_at': url_entry[2].strftime('%Y-%m-%d')
    }

    checks_list = [
        {
            'id': check['id'],
            'url_id': check['url_id'],
            'status_code': check['status_code'],
            'h1': check['h1'],
            'title': check['title'],
            'description': check['description'],
            'created_at': check['created_at']
            if isinstance(check['created_at'], str)
            else check['created_at'].strftime('%Y-%m-%d')
        }
        for check in checks
    ]

    return render_template('url_detail.html', url=url_data, checks=checks_list)


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def run_checks(url_id):
    url_entry = get_url_name_by_id(url_id)

    if url_entry is None:
        return "URL not found", 404

    url_name = url_entry[1]

    if run_check(url_id, url_name):
        flash('Проверка выполнена успешно!', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('url_detail', url_id=url_id))


if __name__ == '__main__':
    app.run(debug=True)
