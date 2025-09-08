from controllers.library_controller import LibraryController
from patterns.factory import BookFactory
from models.user import UserFactory
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    controller = LibraryController()

    book1 = BookFactory.create_book("AncientScript", "Mystic Runes", "Eldoria", "ISBN001", {"language": "Ancient Eldorian", "genre": "Mystical", "preservation": "High"})
    book2 = BookFactory.create_book("RareBook", "Secrets of the Sphinx", "Ibrahim", "ISBN002", {"era": "Antique", "genre": "Historical", "access": "Restricted"})
    book3 = BookFactory.create_book("GeneralBook", "Modern Magic", "Nova", "ISBN003", {"genre": "Fantasy"})
    
    controller.add_book(book1)
    controller.add_book(book2)
    controller.add_book(book3)

    # Flag a book for restoration
    controller.flag_for_restoration(book1, {"rating": 3, "details": {"damage": "faded text"}})

    console.print("\n[bold magenta]Welcome to the Enchanted Library System![/bold magenta]")
    while True:
        console.print("\n[bold cyan]Options:[/bold cyan]")
        console.print("[yellow]1.[/yellow] List all books")
        console.print("[yellow]2.[/yellow] Register new user")
        console.print("[yellow]3.[/yellow] Borrow a book")
        console.print("[yellow]4.[/yellow] Return a book")
        console.print("[yellow]5.[/yellow] Undo last action")
        console.print("[yellow]6.[/yellow] Check overdue books")
        console.print("[yellow]7.[/yellow] Process legacy record")
        console.print("[yellow]8.[/yellow] Recommend books")
        console.print("[yellow]9.[/yellow] View borrowed books")
        console.print("[yellow]10.[/yellow] Flag book for restoration")
        console.print("[yellow]11.[/yellow] Exit")
        
        choice = Prompt.ask("[bold green]Enter your choice (1-11)[/bold green]")
        
        if choice == "1":
            controller.list_books()
        elif choice == "2":
            name = Prompt.ask("Enter new username")
            password = Prompt.ask("Enter new password", password=True)
            console.print("Available roles: [cyan]Librarian[/cyan], [cyan]Scholar[/cyan], [cyan]Guest[/cyan]")
            role = Prompt.ask("Enter role", choices=["Librarian", "Scholar", "Guest"], default="Guest")
            if role not in ["Librarian", "Scholar", "Guest"]:
                console.print("[red]Invalid role![/red]")
                continue
            new_user = UserFactory.create_user(role, name, [])
            controller.register_user(new_user, password)
            console.print(f"[green]User {name} registered successfully as {role}.[/green]")
        elif choice == "3": 
            isbn = Prompt.ask("Enter book ISBN")
            user_name = Prompt.ask("Enter user name")
            lending_type = Prompt.ask("Enter lending type", choices=["public", "academic", "restricted"], default="public")
            user = controller.get_user(user_name)
            if not user:
                console.print(f"[red]User {user_name} not found! Registration Required.[/red]")
                continue
            controller.borrow_book(isbn, user, lending_type)
        elif choice == "4":
            isbn = Prompt.ask("Enter book ISBN")
            user_name = Prompt.ask("Enter user name")
            user = controller.get_user(user_name)
            if not user:
                console.print(f"[red]User {user_name} not found![/red]")
                continue
            controller.return_book(isbn, user)
        elif choice == "5":
            controller.undo_action()
        elif choice == "6":
            controller.check_overdue()
        elif choice == "7":
            record = Prompt.ask("Enter legacy record (format: title;author;isbn;status;type)")
            controller.process_legacy_record(record)
        elif choice == "8":
            user_name = Prompt.ask("Enter user name for recommendations")
            user = controller.get_user(user_name)
            if not user:
                console.print(f"[red]User {user_name} not found![/red]")
                continue
            controller.recommend_books(user)
        elif choice == "9":
            controller.view_borrowed_books()
        elif choice == "10":
            isbn = Prompt.ask("Enter book ISBN to flag for restoration")
            book = controller.facade.catalog.get_book(isbn)
            if not book:
                console.print(f"[red]Book with ISBN {isbn} not found![/red]")
                continue
            rating = int(Prompt.ask("Enter restoration rating (1-10)", default="5"))
            details = Prompt.ask("Enter restoration details (optional)")
            controller.flag_for_restoration(book, {"rating": rating, "details": {"info": details}})
        elif choice == "11":
            console.print("[bold magenta]Thank you for using the Enchanted Library System! Goodbye![/bold magenta]")
            break
        else:
            console.print("[red]Invalid choice! Please select a valid option.[/red]")

if __name__ == "__main__":
    main()
