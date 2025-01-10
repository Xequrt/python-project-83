import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class Database:
    def __init__(self):
        self.connection_pool = pool.SimpleConnectionPool(1, 100, DATABASE_URL)

    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        self.connection_pool.putconn(conn)


db = Database()
