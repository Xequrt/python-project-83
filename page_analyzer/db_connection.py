import os
from psycopg2 import pool, OperationalError
from dotenv import load_dotenv
import time


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def retry(retries=5, interval=1):
    def wrapper(func):
        def inner(*args, **kwargs):
            i = 0
            while i < retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    print(f"Ошибка: {e}, попытка: {i + 1}/{retries}")
                    i += 1
                    if i >= retries:
                        raise
                    time.sleep(interval)

        return inner
    return wrapper


class Database:
    def init(self):
        self.connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)

    @retry(retries=5, interval=1)
    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        self.connection_pool.putconn(conn)


db = Database()
