from models.catalog import Catalog
from models.user import UserFactory
from controllers.preservation import PreservationManager
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

class LibraryFacade:
    def __init__(self):
        self.catalog = Catalog()
        self.preservation_manager = PreservationManager(self.catalog.db)

    def add_new_book(self, book):
        self.catalog.add_book(book)
        console.print(f"[green]Book added:[/green] [bold]{book.title}[/bold] by [cyan]{book.author}[/cyan] (ISBN: {book.isbn}) - Status: [yellow]{book.get_state()}[/yellow]")

    def list_all_books(self):
        books = self.catalog.list_books()
        if books:
            table = Table(title="Available Books")
            table.add_column("Title", style="cyan")
            table.add_column("Author", style="magenta")
            table.add_column("ISBN", style="yellow")
            table.add_column("Status", style="green")
            for book in books:
                table.add_row(book.title, book.author, book.isbn, book.get_state())
            console.print(table)
        else:
            console.print("[red]No books available in the catalog.[/red]")

    def borrow_book(self, isbn, user, strategy, command_manager):
        book = self.catalog.get_book(isbn)
        if book and book.can_borrow():
            strategy.borrow_book(book, user)
            self.catalog.update_book(book)
            query = """
            INSERT INTO borrowing_records (isbn, user_id, borrow_date, due_date)
            VALUES (%s, (SELECT user_id FROM users WHERE name = %s), %s, %s)
            """
            from datetime import datetime, timedelta
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=strategy.get_loan_duration())
            self.catalog.db.execute_query(query, (isbn, user.name, borrow_date, due_date))
            def redo_borrow():
                strategy.borrow_book(book, user)
                self.catalog.update_book(book)
                self.catalog.db.execute_query(query, (isbn, user.name, borrow_date, due_date))
            def undo_borrow():
                from patterns.strategy import PublicLending
                book.set_state(PublicLending().return_book(book))
                self.catalog.update_book(book)
                return_query = """
                UPDATE borrowing_records
                SET return_date = %s
                WHERE isbn = %s AND user_id = (SELECT user_id FROM users WHERE name = %s) AND return_date IS NULL
                """
                self.catalog.db.execute_query(return_query, (datetime.now(), isbn, user.name))
            command_manager.execute(redo_borrow, undo_borrow)
            console.print(f"[green]{book.title} borrowed by {user.name}. Due date: {due_date}[/green]")
        else:
            console.print(f"[red]Cannot borrow {book.title if book else isbn}: current status is {book.get_state() if book else 'not found'}[/red]")

    def return_book(self, isbn, user, command_manager):
        book = self.catalog.get_book(isbn)
        if book:
            from patterns.strategy import PublicLending
            strategy = PublicLending()
            book.set_state(strategy.return_book(book))
            self.catalog.update_book(book)
            query = """
            UPDATE borrowing_records
            SET return_date = %s
            WHERE isbn = %s AND user_id = (SELECT user_id FROM users WHERE name = %s) AND return_date IS NULL
            """
            return_date = datetime.now()
            self.catalog.db.execute_query(query, (return_date, isbn, user.name))
            def redo_return():
                book.set_state(strategy.return_book(book))
                self.catalog.update_book(book)
                self.catalog.db.execute_query(query, (return_date, isbn, user.name))
            def undo_return():
                strategy.borrow_book(book, user)
                self.catalog.update_book(book)
                borrow_query = """
                INSERT INTO borrowing_records (isbn, user_id, borrow_date, due_date)
                VALUES (%s, (SELECT user_id FROM users WHERE name = %s), %s, %s)
                """
                from datetime import datetime, timedelta
                borrow_date = datetime.now()
                due_date = borrow_date + timedelta(days=strategy.get_loan_duration())
                self.catalog.db.execute_query(borrow_query, (isbn, user.name, borrow_date, due_date))
            command_manager.execute(redo_return, undo_return)
            console.print(f"[green]{book.title} returned by {user.name}.[/green]")
        else:
            console.print(f"[red]Book with ISBN {isbn} not found.[/red]")

    def get_user(self, name):
        query = "SELECT * FROM users WHERE name = %s"
        result = self.catalog.db.execute_query(query, (name,))
        if result:
            user_data = result[0]
            return UserFactory.create_user(user_data['role'], user_data['name'], user_data['permissions'])
        return None

    def list_borrowed_books(self):
        query = """
        SELECT b.title, b.author, b.isbn, u.name
        FROM borrowing_records br
        JOIN books b ON br.isbn = b.isbn
        JOIN users u ON br.user_id = u.user_id
        WHERE br.return_date IS NULL
        """
        results = self.catalog.db.execute_query(query)
        if results:
            table = Table(title="Borrowed Books")
            table.add_column("Title", style="cyan")
            table.add_column("Author", style="magenta")
            table.add_column("ISBN", style="yellow")
            table.add_column("Borrower", style="green")
            for record in results:
                table.add_row(record['title'], record['author'], record['isbn'], record['name'])
            console.print(table)
        else:
            console.print("[yellow]No books are currently borrowed.[/yellow]")

    def flag_for_restoration(self, book, condition_report):
        self.preservation_manager.flag_for_restoration(book, condition_report)
        console.print(f"[yellow]{book.title} flagged for restoration.[/yellow]")

    def get_restoration_queue(self):
        return self.preservation_manager.get_restoration_queue()