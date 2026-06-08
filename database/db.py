import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE")
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=DictCursor,
            charset='utf8mb4'
        )
        return self.connection

    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()

    def get_all_places(self):
        return self.execute_query("SELECT * FROM places")

    def get_all_hotels(self):
        return self.execute_query("SELECT * FROM hotels")

    def get_all_restaurants(self):
        return self.execute_query("SELECT * FROM restaurants")

    def get_all_guides(self):
        return self.execute_query("SELECT * FROM guides")

    def get_all_packages(self):
        return self.execute_query("SELECT * FROM packages")