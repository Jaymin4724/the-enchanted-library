from datetime import datetime

def calculate_late_fee(book, strategy):
    if not book.get_due_date():
        return 0
    overdue_days = (datetime.now() - book.get_due_date()).days
    if overdue_days > 0:
        return strategy.calculate_late_fee(overdue_days)
    return 0