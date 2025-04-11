import json
import pandas as pd
from datetime import datetime
from collections import defaultdict
from fpdf import FPDF
import os

def load_expenses(filepath, user_email):
    try:
        with open(filepath, "r") as f:
            data = f.read().strip()
            all_expenses = json.loads(data) if data else []
            return [e for e in all_expenses if e.get("user") == user_email]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_expense(filepath, expense):
    try:
        with open(filepath, "r") as f:
            data = f.read().strip()
            all_expenses = json.loads(data) if data else []
    except (FileNotFoundError, json.JSONDecodeError):
        all_expenses = []

    all_expenses.append(expense)
    with open(filepath, "w") as f:
        json.dump(all_expenses, f, indent=4)

def filter_expenses(expenses, category=None, start_date=None, end_date=None):
    def date_in_range(date_str):
        if start_date and date_str < start_date:
            return False
        if end_date and date_str > end_date:
            return False
        return True

    return [e for e in expenses if
            (not category or e["category"] == category) and
            date_in_range(e["date"])]

def calculate_total(expenses):
    return sum(e["amount"] for e in expenses)

def get_unique_categories(expenses):
    return sorted(set(e["category"] for e in expenses))

def group_expenses_by_year_month(expenses):
    grouped = defaultdict(lambda: defaultdict(list))
    for e in expenses:
        date = datetime.strptime(e["date"], "%Y-%m-%d")
        grouped[date.year][date.strftime("%B")].append(e)
    return dict(grouped)

def get_expenses_by_category(expenses):
    category_totals = defaultdict(float)
    for e in expenses:
        category_totals[e["category"]] += e["amount"]
    return category_totals

def export_to_excel(expenses):
    df = pd.DataFrame(expenses)
    filepath = "data/expenses_export.xlsx"
    df.to_excel(filepath, index=False)
    return filepath

def export_to_pdf(expenses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Expense Report", ln=True, align="C")
    for e in expenses:
        line = f"{e['date']} | ${e['amount']} | {e['category']} | {e['description']}"
        pdf.cell(200, 10, txt=line, ln=True, align="L")
    filepath = "data/expenses_export.pdf"
    pdf.output(filepath)
    return filepath
