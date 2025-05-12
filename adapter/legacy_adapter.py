from models.book import GeneralBook
from patterns.state import AvailableState, BorrowedState, RestorationNeededState
from patterns.factory import BookFactory
from rich.console import Console

console = Console()

class LegacyRecord:
    def __init__(self, record_str):
        if not record_str.count(";") == 4:
            raise ValueError("Invalid legacy record format. Expected: Title;Author;ISBN;Status;Type")
        self.record_str = record_str

class LegacyRecordAdapter:
    def __init__(self, legacy_record: LegacyRecord):
        self.legacy_record = legacy_record

    def get_book(self):
        parts = self.legacy_record.record_str.split(";")
        if len(parts) != 5:
            console.print("[red]Invalid legacy record: incorrect number of fields[/red]")
            raise ValueError("Invalid legacy record: incorrect number of fields")
        title, author, isbn, status, book_type = parts
        book = BookFactory.create_book(book_type, title, author, isbn)
        status_map = {
            "Borrowed": BorrowedState,
            "RestorationNeeded": RestorationNeededState,
            "Available": AvailableState
        }
        state_class = status_map.get(status, AvailableState)
        if state_class == AvailableState and status not in status_map:
            console.print(f"[yellow]Warning: Unknown status '{status}', defaulting to Available[/yellow]")
        book.set_state(state_class())
        return book