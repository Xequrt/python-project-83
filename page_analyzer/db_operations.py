from datetime import datetime
from page_analyzer.db_connection import Database

db = Database()


def get_url_by_name(url_name):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM urls WHERE name = %s', (url_name,))
    result = cursor.fetchone()
    cursor.close()
    db.release_connection(conn)
    return result


def insert_url(url_name):
    conn = db.get_connection()
    cursor = conn.cursor()
    created_at = datetime.now()
    cursor.execute('''
        INSERT INTO urls (name, created_at)
        VALUES (%s, %s) RETURNING id
    ''', (url_name, created_at))
    url_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    db.release_connection(conn)
    return url_id


def get_url_name_by_id(url_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, created_at FROM urls WHERE id = %s', (url_id,)) # noqa: E501
    result = cursor.fetchone()
    cursor.close()
    db.release_connection(conn)
    return result


def get_all_urls():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.created_at, uc.status_code
        FROM urls u
        LEFT JOIN url_checks uc ON u.id = uc.url_id
        WHERE uc.id = (
            SELECT MAX(id) FROM url_checks WHERE url_id = u.id)
        OR uc.id IS NULL
        ORDER BY u.created_at DESC
    ''')
    all_urls = cursor.fetchall()
    cursor.close()
    db.release_connection(conn)

    urls_list = [{'id': url[0], 'name': url[1],
                  'created_at': url[2].strftime('%Y-%m-%d'),
                  'status_code': url[3] if url[3] is not None else ''}
                 for url in all_urls]
    return urls_list


def get_url_checks(url_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM url_checks WHERE url_id = %s', (url_id,))
    checks = cursor.fetchall()
    cursor.close()
    db.release_connection(conn)

    checks_list = [
        {
            'id': check[0],
            'url_id': check[1],
            'status_code': check[2],
            'h1': check[3],
            'title': check[4],
            'description': check[5],
            'created_at': check[6].strftime('%Y-%m-%d')
        }
        for check in checks
    ]
    return checks_list
