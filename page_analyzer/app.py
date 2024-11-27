# from flask import render_template
from page_analyzer import app


@app.route('/')
@app.route('/index')
def hello():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
