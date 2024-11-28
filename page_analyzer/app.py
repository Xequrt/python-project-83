# from flask import render_template
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello():
    return "Hello, World!"


if __name__ == '__main__':
    app.run()
