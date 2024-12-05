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
    if cursor.fetchone():
        flash('Этот URL уже добавлен.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    created_at = datetime.now()
    cursor.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s)', (normalized_url, created_at))
    conn.commit()
    cursor.close()
    conn.close()
    flash('URL успешно добавлен!', 'success')
    return redirect(url_for('urls'))


@app.route('/urls')
def urls():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM urls ORDER BY created_at DESC')
    all_urls = cursor.fetchall()

    urls_list = [{'id': url[0], 'name': url[1], 'created_at': url[2]} for url in all_urls]

    cursor.close()
    conn.close()
    return render_template('urls.html', urls=urls_list)

@app.route('/urls/<int:url_id>')
def url_detail(url_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM urls WHERE id = %s', (url_id,))
    url_entry = cursor.fetchone()
    cursor.close()
    conn.close()
    if url_entry is None:
        return "URL not found", 404
    url_data = {
        'id': url_entry[0],
        'name': url_entry[1],
        'created_at': url_entry[2]
    }
    return render_template('url_detail.html', url=url_data)

if __name__ == '__main__':
    app.run(debug=True)
