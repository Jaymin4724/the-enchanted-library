from database.database import Database
from models.book import GeneralBook, RareBook, AncientScript
from psycopg2.extras import Json
from patterns.state import AvailableState, BorrowedState, RestorationNeededState

class Catalog:
    def __init__(self):
        self.db = Database()
        self.books = {}

    def add_book(self, book):
        self.books[book.isbn] = book
        query = """
        INSERT INTO books (isbn, title, author, status, metadata)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (isbn) DO UPDATE
        SET title = EXCLUDED.title,
            author = EXCLUDED.author,
            status = EXCLUDED.status,
            metadata = EXCLUDED.metadata
        """
        self.db.execute_query(query, (
            book.isbn,
            book.title,
            book.author,
            book.get_state(),
            Json(book.metadata)
        ))

    def get_book(self, isbn):
        if isbn in self.books:
            return self.books[isbn]
        query = "SELECT * FROM books WHERE isbn = %s"
        result = self.db.execute_query(query, (isbn,))
        if result:
            book_data = result[0]
            metadata = book_data['metadata']
            # Determine book type from metadata or default to GeneralBook
            book_type = metadata.get('access', 'General')
            if book_type == 'Restricted':
                book = RareBook(book_data['title'], book_data['author'], book_data['isbn'], metadata)
            elif book_type == 'Preserved':
                book = AncientScript(book_data['title'], book_data['author'], book_data['isbn'], metadata)
            else:
                book = GeneralBook(book_data['title'], book_data['author'], book_data['isbn'], metadata)
            state_map = {
                'Available': AvailableState(),
                'Borrowed': BorrowedState(),
                'Restoration Needed': RestorationNeededState()
            }
            book.set_state(state_map.get(book_data['status'], AvailableState()))
            self.books[isbn] = book
            return book
        return None

    def update_book(self, book):
        self.books[book.isbn] = book
        query = """
        UPDATE books
        SET title = %s, author = %s, status = %s, metadata = %s
        WHERE isbn = %s
        """
        self.db.execute_query(query, (
            book.title,
            book.author,
            book.get_state(),
            Json(book.metadata),
            book.isbn
        ))

    def list_books(self):
        query = "SELECT * FROM books"
        results = self.db.execute_query(query)
        books = []
        for book_data in results:
            book = self.get_book(book_data['isbn'])
            if book:
                books.append(book)
        return books