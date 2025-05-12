from abc import ABC, abstractmethod

class BookState(ABC):
    @abstractmethod
    def can_borrow(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

class AvailableState(BookState):
    def can_borrow(self):
        return True

    def __str__(self):
        return "Available"

class BorrowedState(BookState):
    def can_borrow(self):
        return False

    def __str__(self):
        return "Borrowed"

class RestorationNeededState(BookState):
    def can_borrow(self):
        return False

    def __str__(self):
        return "Restoration Needed"