import os
from psycopg2 import pool, OperationalError
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class Database:
    def __init__(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)
        except OperationalError as e:
            print(f"Ошибка при создании соединения: {e}")

    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        self.connection_pool.putconn(conn)


db = Database()
