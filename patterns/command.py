from abc import ABC, abstractmethod
import copy
from patterns.state import BorrowedState, AvailableState
from utils.utils import calculate_late_fee
from rich.console import Console
from models.catalog import Catalog
from database.database import Database
from patterns.strategy import PublicLending

console = Console()

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class GenericCommand(Command):
    def __init__(self, redo_action, undo_action):
        self.redo_action = redo_action
        self.undo_action = undo_action

    def execute(self):
        self.redo_action()

    def undo(self):
        self.undo_action()

class BorrowCommand(Command):
    def __init__(self, book, user, strategy):
        self.book = book
        self.user = user
        self.strategy = strategy
        self.prev_state = copy.deepcopy(book._state)
        self.prev_due_date = book.get_due_date()

    def execute(self):
        if self.book.get_state() == "Available" and self.strategy.can_borrow(self.user):
            self.book.set_state(BorrowedState())
            self.book.set_due_date(self.strategy.calculate_due_date())
            Catalog().update_book(self.book)
            print(f"{self.user.name} borrowed {self.book.title}, due on {self.book.get_due_date().strftime('%Y-%m-%d')}")
        else:
            print("Book is not available or user lacks permission.")

    def undo(self):
        self.book.set_state(self.prev_state)
        self.book.set_due_date(self.prev_due_date)
        Catalog().update_book(self.book)
        print(f"Undo borrowing of {self.book.title}")

class ReturnCommand(Command):
    def __init__(self, book, user):
        self.book = book
        self.user = user
        self.prev_state = copy.deepcopy(book._state)
        self.prev_due_date = book.get_due_date()

    def execute(self):
        if self.book.get_state() == "Borrowed":
            fee = calculate_late_fee(self.book, PublicLending())
            if fee > 0:
                db = Database()
                db.connect()
                query = """
                UPDATE borrowing_records
                SET late_fee = %s
                WHERE isbn = %s AND user_id = (SELECT user_id FROM users WHERE name = %s) AND return_date IS NULL
                """
                db.execute_query(query, (fee, self.book.isbn, self.user.name))
            self.book.set_state(AvailableState())
            self.book.set_due_date(None)
            Catalog().update_book(self.book)
            print(f"{self.user.name} returned {self.book.title}")
        else:
            print("Book was not borrowed.")

    def undo(self):
        self.book.set_state(self.prev_state)
        self.book.set_due_date(self.prev_due_date)
        Catalog().update_book(self.book)
        print(f"Undo return of {self.book.title}")

class CommandManager:
    def __init__(self):
        self.history = []
        self.max_history = 100

    def execute(self, redo_action, undo_action):
        command = GenericCommand(redo_action, undo_action)
        self.execute_command(command)

    def execute_command(self, command):
        command.execute()
        self.history.append(command)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo_last(self):
        if self.history:
            command = self.history.pop()
            command.undo()
            console.print("[yellow]Last action undone.[/yellow]")
        else:
            console.print("[red]No actions to undo.[/red]")