from abc import ABC, abstractmethod

class User(ABC):
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions if permissions else []
        self.reading_history = []

    @abstractmethod
    def role(self):
        pass

    def has_permission(self, permission):
        return permission in self.permissions

    def add_to_history(self, book):
        self.reading_history.append(book)

class Librarian(User):
    def role(self):
        return "Librarian"

    def update(self, book):
        print(f"Librarian {self.name} notified: {book.title} status changed to {book.get_state()}")

class Scholar(User):
    def role(self):
        return "Scholar"

class Guest(User):
    def role(self):
        return "Guest"

class UserFactory:
    @staticmethod
    def create_user(role, name, permissions):
        role_map = {
            "Librarian": Librarian,
            "Scholar": Scholar,
            "Guest": Guest
        }
        user_class = role_map.get(role, Guest)  # Default to Guest if role is unknown
        return user_class(name, permissions)
