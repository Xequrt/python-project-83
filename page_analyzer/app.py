from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


url_data = {}


@app.route('/')
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']
    url_id = len(url_data) + 1
    url_data[url_id] = url
    return redirect(url_for('url_detail', url_id=url_id))


@app.route('/urls/<int:url_id>')
def url_detail(url_id):
    url = url_data.get(url_id)
    if url is None:
        return "URL не найден", 404
    return render_template('url_detail.html', url=url, url_id=url_id)


if __name__ == '__main__':
    app.run()
