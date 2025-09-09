# The Enchanted Library

**An Intelligent and Secure Book Management System**

## Overview

The Enchanted Library is a robust, OOP-driven library management system designed to handle ancient manuscripts, rare books, and modern texts. It features secure user authentication, advanced cataloging, role-based access, and automated preservation workflows, all built with Python and PostgreSQL.

---

## Demo Video :

**url** : https://drive.google.com/file/d/137rnurUUDk4TdNuWVpTsJkNGUKTQ_IEW/view?usp=drive_link

---

## Tech Stack

- **Language:** Python 3
- **Database:** PostgreSQL
- **Libraries:** `rich` (CLI UI), `psycopg2` (DB), `bcrypt` (security)
- **Design Patterns:** Factory, Singleton, Builder, Facade, Adapter, Decorator, Observer, Strategy, Command, State

---

## Key Features

- **Role-Based Access Control:** Librarian, Scholar, and Guest roles with granular permissions.
- **Book Cataloging:** Add, update, and track books with metadata (genre, preservation, access).
- **Borrowing & Returns:** Multiple lending strategies (public, academic, restricted).
- **Automated Late Fee Calculation:** Dynamic fee computation based on book type and delay.
- **Preservation & Restoration:** Flag books for restoration, track condition reports.
- **Smart Recommendations:** Suggest books based on user reading history and research topics.
- **Legacy Integration:** Adapter pattern to import handwritten/legacy records.
- **Undo Actions:** Command pattern for undoing borrow/return mistakes.
- **Overdue Reminders:** Decorator pattern for dynamic notifications.

---

# Folder Structure (Overview)

```
main.py
adapter/
   legacy_adapter.py
controllers/
   library_controller.py
   preservation.py
database/
   database.py
facade/
   library_facade.py
models/
   book.py
   catalog.py
   user.py
patterns/
   command.py
   factory.py
   state.py
   strategy.py
utils/
   utils.py
```

## System Architecture

- **main.py:** Entry point, user menu, and CLI.
- **Controller:** Coordinates requests, enforces business logic.
- **Facade:** Unified interface to subsystems (catalog, users, DB, notifications).
- **Patterns:** Modular, maintainable, and extensible codebase.

**Flow Example:**
```
User (main.py) → Controller → Facade → Catalog/DB/Patterns → Controller → User
```

---

## Design Patterns Used

- **Factory:** Create users/books dynamically.
- **Singleton:** Single DB instance.
- **Builder:** Flexible book creation with metadata.
- **Facade:** Unified access to all features.
- **Adapter:** Import legacy records.
- **Decorator:** Add overdue reminders.
- **Observer:** Notify librarians on book state changes.
- **Strategy:** Multiple lending rules.
- **Command:** Undo/redo actions.
- **State:** Book status management.

---

## Quick Start

1. **Clone the repo:**
   ```sh
   git clone https://github.com/Jaymin4724/the-enchanted-library.git
   cd the-enchanted-library
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure PostgreSQL:**
   - Edit `database/database.py` with your DB credentials.
   - Run the SQL setup in the README to create tables.

4. **Run the app:**
   ```sh
   python main.py
   ```

---

## Database Schema

- **books:** ISBN, title, author, status, metadata (JSON)
- **users:** user_id, name, role, permissions (JSON), password (hashed)
- **borrowing_records:** record_id, isbn, user_id, borrow_date, due_date, return_date, late_fee
- **condition_reports:** report_id, isbn, rating, details (JSON), report_date

---

## Example Usage

- **Register User:** Choose role (Librarian, Scholar, Guest)
- **Borrow Book:** Select lending type (public, academic, restricted)
- **Return Book:** Handles late fees automatically
- **Flag for Restoration:** Track book condition and restoration queue
- **Undo Last Action:** Revert mistaken borrow/return
- **Import Legacy Record:** Add books from old handwritten logs

---

## Why This Project Stands Out

- **Clean OOP Design:** Demonstrates mastery of advanced OOP and design patterns.
- **Security:** Passwords hashed, role-based permissions.
- **Extensible:** Easy to add new features or integrate with other systems.
- **Professional CLI:** User-friendly, visually appealing interface.
