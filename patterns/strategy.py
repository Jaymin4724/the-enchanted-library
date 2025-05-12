from abc import ABC, abstractmethod
from patterns.state import AvailableState, BorrowedState
from datetime import datetime, timedelta

class BorrowingStrategy(ABC):
    @abstractmethod
    def borrow_book(self, book, user):
        pass

    @abstractmethod
    def return_book(self, book):
        pass

    @abstractmethod
    def get_loan_duration(self):
        pass

class PublicLending(BorrowingStrategy):
    def borrow_book(self, book, user):
        book.set_state(BorrowedState())
        book.set_due_date(datetime.now() + timedelta(days=14))

    def return_book(self, book):
        return AvailableState()

    def get_loan_duration(self):
        return 14

class AcademicBorrowing(BorrowingStrategy):
    def borrow_book(self, book, user):
        book.set_state(BorrowedState())
        book.set_due_date(datetime.now() + timedelta(days=30))

    def return_book(self, book):
        return AvailableState()

    def get_loan_duration(self):
        return 30

class RestrictedReadingRoom(BorrowingStrategy):
    def borrow_book(self, book, user):
        book.set_state(BorrowedState())
        book.set_due_date(datetime.now() + timedelta(hours=2))

    def return_book(self, book):
        return AvailableState()

    def get_loan_duration(self):
        return 0.083  # 2 hours in days