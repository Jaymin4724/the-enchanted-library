from datetime import datetime
from rich.console import Console
from patterns.state import RestorationNeededState, AvailableState, BorrowedState
from psycopg2.extras import Json

console = Console()

class PreservationManager:
    def __init__(self, db):
        self._restoration_queue = []
        self._db = db

    def flag_for_restoration(self, book, condition_report):
        rating = condition_report.get('rating')
        details = condition_report.get('details', {})
        if not isinstance(rating, int) or not 1 <= rating <= 10:
            console.print("[red]Rating must be an integer between 1 and 10.[/red]")
            raise ValueError("Rating must be an integer between 1 and 10.")
        book.set_state(RestorationNeededState())
        self._restoration_queue.append(book)
        query = """
        INSERT INTO condition_reports (isbn, rating, details, report_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (isbn) DO UPDATE
        SET rating = EXCLUDED.rating,
            details = EXCLUDED.details,
            report_date = EXCLUDED.report_date
        """
        self._db.execute_query(query, (
            book.isbn,
            rating,
            Json(details),
            datetime.now()
        ))
        console.print(f"[yellow]{book.title} flagged for restoration with rating {rating}.[/yellow]")

    def get_restoration_queue(self):
        queue = []
        for book in self._restoration_queue:
            if isinstance(book.get_state(), RestorationNeededState):
                queue.append(book)
        return queue