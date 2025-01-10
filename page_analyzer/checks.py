from db_connection import db
from url_checks import run_all_checks
from datetime import datetime


def run_check(url_id, url_name):
    conn = db.get_connection()
    cursor = conn.cursor()

    results = run_all_checks(url_name)

    status_code = results.get('status_code')
    h1 = results.get('h1')
    title = results.get('title')
    description = results.get('description')

    if status_code is None:
        return False

    try:
        cursor.execute('''
            INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES
            (%s, %s, %s, %s, %s, %s)
        ''', (url_id, status_code, h1, title, description, datetime.now()))

        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        return False
    finally:
        cursor.close()
        db.release_connection(conn)
