from models.book import AncientScript, RareBook, GeneralBook

# Builder for customized book entries
class BookBuilder:
    def __init__(self):
        self.title = None
        self.author = None
        self.isbn = None
        self.metadata = {}

    def set_title(self, title):
        self.title = title
        return self

    def set_author(self, author):
        self.author = author
        return self

    def set_isbn(self, isbn):
        self.isbn = isbn
        return self

    def add_metadata(self, key, value):
        self.metadata[key] = value
        return self

    def build(self, book_type="General"):
        if book_type == "AncientScript":
            return AncientScript(self.title, self.author, self.isbn, self.metadata)
        elif book_type == "RareBook":
            return RareBook(self.title, self.author, self.isbn, self.metadata)
        else:
            return GeneralBook(self.title, self.author, self.isbn, self.metadata)

class BookFactory:
    @staticmethod
    def create_book(book_type, title, author, isbn, metadata=None):
        builder = BookBuilder().set_title(title).set_author(author).set_isbn(isbn)
        if metadata:
            for key, value in metadata.items():
                builder.add_metadata(key, value)
        return builder.build(book_type)
