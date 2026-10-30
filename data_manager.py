"""Handles all reading, writing and calculating of expense data (pandas + numpy)."""

import os
import numpy as np
import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.csv")
COLUMNS = ["Date", "Category", "Description", "Amount"]
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
ALL_TIME = "All Time"


def load_expenses():
    """Load expenses from the CSV file (creates an empty one if missing)."""
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Date", "Amount"]).reset_index(drop=True)
    return df


def save_expenses(df):
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_FILE, index=False)


def add_expense(date, category, description, amount):
    df = load_expenses()
    new_row = pd.DataFrame([{
        "Date": pd.to_datetime(date),
        "Category": category,
        "Description": description,
        "Amount": float(amount),
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_expenses(df)


def delete_expenses(indexes):
    df = load_expenses()
    df = df.drop(index=indexes).reset_index(drop=True)
    save_expenses(df)


def get_months(df):
    """Return the months that have data, newest first, e.g. ['2026-10', '2026-09']."""
    if df.empty:
        return []
    months = df["Date"].dt.strftime("%Y-%m").unique().tolist()
    return sorted(months, reverse=True)


def filter_by_month(df, month):
    """Keep only rows of one month ('YYYY-MM'). 'All Time' returns everything.
    The original row numbers are kept so delete still works on a filtered view."""
    if month == ALL_TIME or df.empty:
        return df
    return df[df["Date"].dt.strftime("%Y-%m") == month]


def get_summary(df):
    """Return key numbers using numpy."""
    if df.empty:
        return {"total": 0.0, "average": 0.0, "highest": 0.0, "count": 0, "top_category": "-"}
    amounts = df["Amount"].to_numpy()
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    return {
        "total": float(np.sum(amounts)),
        "average": float(np.mean(amounts)),
        "highest": float(np.max(amounts)),
        "count": int(len(amounts)),
        "top_category": top_category,
    }