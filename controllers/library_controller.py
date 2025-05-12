import bcrypt
from facade.library_facade import LibraryFacade
from patterns.strategy import AcademicBorrowing, PublicLending, RestrictedReadingRoom
from patterns.command import CommandManager
from models.book import BookDecorator
from utils.utils import calculate_late_fee
from psycopg2.extras import Json
from rich.console import Console
from rich.table import Table

console = Console()

def smart_book_recommendations(user, catalog):
    if not user.reading_history:
        recommendations = [book for book in catalog.list_books() if book.get_state() == "Available"]
    else:
        recommendations = [book for book in catalog.list_books() if book.get_state() == "Available" and 
                          any(book.author == hist.author or book.metadata.get('genre') == hist.metadata.get('genre') 
                              for hist in user.reading_history)]
    table = Table(title=f"Recommendations for {user.name}")
    table.add_column("Title", style="cyan")
    table.add_column("Author", style="magenta")
    for book in recommendations:
        table.add_row(book.title, book.author)
    console.print(table)

class LibraryController:
    def __init__(self):
        self.facade = LibraryFacade()
        # self.view = LibraryView()
        self.command_manager = CommandManager()
        self.librarians = []

    def add_librarian(self, librarian):
        self.librarians.append(librarian)
        for book in self.facade.catalog.list_books():
            book.add_observer(librarian)

    def register_user(self, user, password):
        # Assign default permissions based on role
        role_permissions = {
            "Librarian": ["manage_books", "notify_overdue", "access_all"],
            "Scholar": ["borrow_books", "access_restricted"],
            "Guest": ["borrow_books"]
        }
        user.permissions = role_permissions.get(user.role(), ["borrow_books"])
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = """
        INSERT INTO users (name, role, permissions, password)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name) DO NOTHING
        """
        self.facade.catalog.db.execute_query(query, (
            user.name,
            user.role(),
            Json(user.permissions),
            hashed_password
        ))

    def get_user(self, name):
        return self.facade.get_user(name)

    def add_book(self, book):
        self.facade.add_new_book(book)
        for librarian in self.librarians:
            book.add_observer(librarian)

    def list_books(self):
        self.facade.list_all_books()

    def borrow_book(self, isbn, user, lending_type="public"):
        book = self.facade.catalog.get_book(isbn)
        if not book:
            console.print(f"[red]Book with ISBN {isbn} not found![/red]")
            return
        if not book.can_borrow():
            console.print(f"[red]Book '{book.title}' is not available for borrowing![/red]")
            return
        if book.metadata.get('access') == "Restricted" and not user.has_permission("access_restricted"):
            console.print(f"[red]User {user.name} does not have permission to access restricted books![/red]")
            return
        if lending_type.lower() == "academic":
            strategy = AcademicBorrowing()
        elif lending_type.lower() == "restricted":
            strategy = RestrictedReadingRoom()
        else:
            strategy = PublicLending()
        self.facade.borrow_book(isbn, user, strategy, self.command_manager)
        user.add_to_history(book)

    def return_book(self, isbn, user):
        book = self.facade.catalog.get_book(isbn)
        if book:
            strategy = PublicLending()
            fee = calculate_late_fee(book, strategy)
            if fee > 0:
                console.print(f"Late fee for {book.title}: ${fee:.2f}")
                query = """
                UPDATE borrowing_records
                SET late_fee = %s
                WHERE isbn = %s AND user_id = (SELECT user_id FROM users WHERE name = %s) AND return_date IS NULL
                """
                self.facade.catalog.db.execute_query(query, (fee, isbn, user.name))
            self.facade.return_book(isbn, user, self.command_manager)
        else:
            console.print("[red]Book not found in catalog.[/red]")

    def undo_action(self):
        self.command_manager.undo_last()

    def check_overdue(self):
        for book in self.facade.catalog.list_books():
            decorated = BookDecorator(book)
            decorated.send_overdue_reminder()
            strategy = PublicLending()
            fee = calculate_late_fee(book, strategy)
            if fee > 0:
                console.print(f"Late fee for {book.title}: ${fee:.2f}")

    def process_legacy_record(self, record_str):
        from adapter.legacy_adapter import LegacyRecordAdapter, LegacyRecord
        try:
            legacy_record = LegacyRecord(record_str)
            adapter = LegacyRecordAdapter(legacy_record)
            book = adapter.get_book()
            self.add_book(book)
        except ValueError as e:
            console.print(f"[red]Error processing legacy record: {e}[/red]")

    def recommend_books(self, user):
        user_db = self.get_user(user.name)
        if user_db:
            smart_book_recommendations(user_db, self.facade.catalog)
        else:
            console.print(f"[red]User {user.name} not found.[/red]")

    def view_borrowed_books(self):
        self.facade.list_borrowed_books()

    def flag_for_restoration(self, book, condition_report):
        if book:
            try:
                rating = condition_report.get('rating')
                if not isinstance(rating, int) or not 1 <= rating <= 10:
                    raise ValueError("Rating must be an integer between 1 and 10.")
                self.facade.flag_for_restoration(book, condition_report)
            except ValueError as e:
                console.print(f"[red]Error flagging book for restoration: {e}[/red]")
        else:
            console.print("[red]Book not found in catalog.[/red]")

    def view_restoration_queue(self):
        queue = self.facade.get_restoration_queue()
        if queue:
            console.print("\n--- Restoration Queue ---")
            for book in queue:
                console.print(book)
        else:
            console.print("[red]No books in restoration queue.[/red]")