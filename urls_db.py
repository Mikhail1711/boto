import sqlite3
import string
import random


class Urls:
    _instance = None
    connection = sqlite3.connect('short_urls.db', check_same_thread=False)
    cursor = connection.cursor()


    def __new__(cls, *args, **kvargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def __del__(self):
        Urls._instance = None


    def __init__(self, db_path='short_urls.db'):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                short TEXT PRIMARY KEY CHECK(length(short) <= 10),
                large TEXT CHECK(length(large) <= 1000)
            )
        ''')
        self.connection.commit()


    def close(self):
        self.connection.close()


    @classmethod
    def generate_short(cls, lenght=10):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(lenght))


    def create_pair(self, large):
        short = self.generate_short()
        while self.get_url(short) != '':
            short = self.generate_short()


        query = '''
                INSERT OR IGNORE INTO urls 
                (short, large) 
                VALUES (?, ?)
        '''
        self.cursor.execute(query, (short, large))
        self.connection.commit()
        return short


    def get_url(self, short):
        query = '''SELECT large FROM urls WHERE short = ?'''
        large = self.cursor.execute(query, (short,)).fetchone()
        return large[0] if large else ''
    

    def delete_pair(self, short):
        query = '''DELETE FROM urls WHERE short = ?'''
        self.cursor.execute(query, (short,))
        self.connection.commit()
