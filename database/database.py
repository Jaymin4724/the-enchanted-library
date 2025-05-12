import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._conn = None
        self._cursor = None
        try:
            self._conn = psycopg2.connect(
                dbname="Enchanted Library",
                user="postgres",
                password="jaymin4724",  # Replace with your PostgreSQL password
                host="localhost",
                port="5433"
            )
            self._cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        except psycopg2.Error as e:
            raise Exception(f"Failed to connect to database: {e}")
        self._initialized = True

    def execute_query(self, query, params=()):
        if self._cursor is None:
            raise Exception("Database cursor is not initialized. Connection failed.")
        try:
            self._cursor.execute(query, params)
            self._conn.commit()
            if query.strip().upper().startswith("SELECT"):
                return self._cursor.fetchall()
            return []
        except psycopg2.Error as e:
            self._conn.rollback()
            raise Exception(f"Query execution failed: {e}")

    def is_connected(self):
        return self._conn is not None and not self._conn.closed

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()