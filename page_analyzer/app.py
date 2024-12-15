import requests
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
from dotenv import load_dotenv
import validators
from urllib.parse import urlparse
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/')
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']

    parsed_url = urlparse(url)
    normalized_url = parsed_url.geturl()

    if not validators.url(normalized_url) or len(normalized_url) > 255:
        flash('Некорректный URL. Пожалуйста, введите действительный URL-адрес, не превышающий 255 символов.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM urls WHERE name = %s', (normalized_url,))
    existing_url = cursor.fetchone()
    if existing_url:
        flash('Страница уже существует', 'info')
        url_id = existing_url[0]
    else:
        created_at = datetime.now()
        cursor.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id', (normalized_url, created_at))
        url_id = cursor.fetchone()[0]
        conn.commit()
        flash('Страница успешно добавлена!', 'success')
        # cursor.execute("INSERT INTO url_checks (url_id, created_at) VALUES (%s, CURRENT_TIMESTAMP)", (url_id,))
        # conn.commit()

        cursor.close()
        conn.close()

        # Перенаправляем на страницу деталей URL
    return redirect(url_for('url_detail', url_id=url_id))


@app.route('/urls')
def urls():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT u.id, u.name, u.created_at, uc.status_code
    FROM urls u
    LEFT JOIN url_checks uc ON u.id = uc.url_id
    WHERE uc.id = (
    SELECT MAX(id) FROM url_checks WHERE url_id = u.id)
    ORDER BY u.created_at DESC
    ''')
    all_urls = cursor.fetchall()

    urls_list = [{'id': url[0], 'name': url[1], 'created_at': url[2].strftime('%Y-%m-%d'), 'status_code': url[3]} for url in all_urls]

    cursor.close()
    conn.close()
    return render_template('urls.html', urls=urls_list)

@app.route('/urls/<int:url_id>')
def url_detail(url_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM urls WHERE id = %s', (url_id,))
    url_entry = cursor.fetchone()
    if url_entry is None:
        return "URL not found", 404

    cursor.execute('SELECT * FROM url_checks WHERE url_id = %s', (url_id,))
    checks = cursor.fetchall()

    cursor.close()
    conn.close()

    url_data = {
        'id': url_entry[0],
        'name': url_entry[1],
        'created_at': url_entry[2].strftime('%Y-%m-%d')
    }

    checks_list = [{'id': check[0], 'url_id': check[1], 'status_code': check[2], 'created_at': check[6].strftime('%Y-%m-%d')} for check in checks]

    return render_template('url_detail.html', url=url_data, checks=checks_list)

@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def run_checks(url_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM urls WHERE id = %s', (url_id,))
    url_entry = cursor.fetchone()

    if url_entry is None:
        return "URL not found", 404

    url_data = {
        'id': url_entry[0],
        'name': url_entry[1],
        'created_at': url_entry[2].strftime('%Y-%m-%d')
    }

    try:
        response = requests.get(url_data['name'])
        response.raise_for_status()
        status_code = response.status_code

        cursor.execute("INSERT INTO url_checks (url_id, status_code, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)", (url_id, status_code))

        conn.commit()

        flash('Проверка выполнена успешно!', 'success')
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('url_detail', url_id=url_id))

if __name__ == '__main__':
    app.run(debug=True)
