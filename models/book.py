from abc import ABC
from patterns.state import AvailableState
from rich.console import Console

console = Console()

class Book(ABC):
    def __init__(self, title, author, isbn, metadata):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.metadata = metadata if metadata else {}
        self._state = AvailableState()
        self._observers = []
        self._due_date = None

    def set_state(self, state):
        self._state = state
        self.notify_observers()

    def get_state(self):
        return str(self._state)

    def can_borrow(self):
        return self._state.can_borrow()

    def set_due_date(self, due_date):
        self._due_date = due_date

    def get_due_date(self):
        return self._due_date

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update(self)

    def __str__(self):
        return f"[bold]{self.title}[/bold] by [cyan]{self.author}[/cyan] (ISBN: {self.isbn})"

class GeneralBook(Book):
    pass

class RareBook(Book):   
    def can_borrow(self):
        return super().can_borrow() and self.metadata.get('access') != "Restricted"

class AncientScript(Book):
    def can_borrow(self):
        return super().can_borrow() and self.metadata.get('preservation') != "High"

class BookDecorator:
    def __init__(self, book):
        self.book = book

    def send_overdue_reminder(self):
        from datetime import datetime
        if self.book.get_due_date() and self.book.get_due_date() < datetime.now():
            console.print(f"[red]Overdue reminder: {self.book.title} is past due![/red]")
