"""Personal Expense Tracker - run this file to start the app."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import data_manager as dm
from charts import draw_charts

BG = "#F1F5F9"
PRIMARY = "#4F46E5"
CARD = "#FFFFFF"
TEXT = "#1E293B"


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        root.title("Personal Expense Tracker")
        root.geometry("1150x700")
        root.configure(bg=BG)
        self.month_var = tk.StringVar(value=dm.ALL_TIME)
        self.setup_style()
        self.build_header()
        self.build_summary_cards()
        self.build_body()
        self.refresh()

    # ---------- styling ----------
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background=PRIMARY, foreground="white")
        style.map("Treeview.Heading", background=[("active", PRIMARY)])
        style.configure("TCombobox", padding=4)

    # ---------- layout ----------
    def build_header(self):
        header = tk.Frame(self.root, bg=PRIMARY, height=60)
        header.pack(fill="x")
        tk.Label(header, text="Personal Expense Tracker", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=12)

        # Month selector (monthly view)
        picker = tk.Frame(header, bg=PRIMARY)
        picker.pack(side="right", padx=20)
        tk.Label(picker, text="View:", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 6))
        self.month_box = ttk.Combobox(picker, textvariable=self.month_var, state="readonly",
                                      width=16, values=[dm.ALL_TIME])
        self.month_box.pack(side="left")
        self.month_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

    def build_summary_cards(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=15, pady=(12, 4))
        self.card_vars = {}
        for key, title in [("total", "Total Spent"), ("average", "Average / Expense"),
                           ("highest", "Highest Expense"), ("top_category", "Top Category")]:
            card = tk.Frame(row, bg=CARD, padx=15, pady=8)
            card.pack(side="left", expand=True, fill="x", padx=5)
            tk.Label(card, text=title, bg=CARD, fg="#64748B", font=("Segoe UI", 9)).pack(anchor="w")
            var = tk.StringVar(value="-")
            tk.Label(card, textvariable=var, bg=CARD, fg=PRIMARY,
                     font=("Segoe UI", 15, "bold")).pack(anchor="w")
            self.card_vars[key] = var

    def build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=15, pady=8)

        # Left side: form + table
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        form = tk.LabelFrame(left, text=" Add New Expense ", bg=CARD, fg=TEXT,
                             font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        form.pack(fill="x")

        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        self.cat_var = tk.StringVar(value=dm.CATEGORIES[0])
        self.desc_var = tk.StringVar()
        self.amount_var = tk.StringVar()

        fields = [("Date (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.date_var, width=16)),
                  ("Category", ttk.Combobox(form, textvariable=self.cat_var, values=dm.CATEGORIES,
                                            state="readonly", width=14)),
                  ("Description", ttk.Entry(form, textvariable=self.desc_var, width=20)),
                  ("Amount (Rs.)", ttk.Entry(form, textvariable=self.amount_var, width=12))]
        for col, (label, widget) in enumerate(fields):
            tk.Label(form, text=label, bg=CARD, fg=TEXT, font=("Segoe UI", 9)).grid(
                row=0, column=col, sticky="w", padx=5)
            widget.grid(row=1, column=col, padx=5, pady=(0, 4))

        btns = tk.Frame(form, bg=CARD)
        btns.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        tk.Button(btns, text="Add Expense", bg=PRIMARY, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=4,
                  command=self.add_expense).pack(side="left", padx=5)
        tk.Button(btns, text="Delete Selected", bg="#EF4444", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=4,
                  command=self.delete_selected).pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(left, bg=BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))
        cols = ("Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="extended")
        for c, w in zip(cols, (95, 105, 190, 85)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center" if c != "Description" else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Right side: charts
        right = tk.Frame(body, bg=CARD)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))
        self.fig = Figure(figsize=(5, 6), dpi=95, facecolor=CARD)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- actions ----------
    def add_expense(self):
        try:
            date = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Please enter the date as YYYY-MM-DD.")
            return
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter a positive number for amount.")
            return

        description = self.desc_var.get().strip() or "-"
        dm.add_expense(date, self.cat_var.get(), description, amount)
        self.desc_var.set("")
        self.amount_var.set("")

        # Jump to the month of the expense just added so the user sees it
        if self.month_var.get() != dm.ALL_TIME:
            self.month_var.set(date.strftime("%Y-%m"))
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nothing selected", "Select one or more rows to delete.")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(selected)} expense(s)?"):
            dm.delete_expenses([int(i) for i in selected])
            self.refresh()

    def refresh(self):
        full_df = dm.load_expenses()

        # update the month dropdown with months that have data
        months = dm.get_months(full_df)
        self.month_box["values"] = [dm.ALL_TIME] + months
        if self.month_var.get() not in [dm.ALL_TIME] + months:
            self.month_var.set(dm.ALL_TIME)

        selected_month = self.month_var.get()
        df = dm.filter_by_month(full_df, selected_month)
        monthly_view = selected_month != dm.ALL_TIME

        # table (newest first)
        self.tree.delete(*self.tree.get_children())
        for idx, row in df.sort_values("Date", ascending=False).iterrows():
            self.tree.insert("", "end", iid=str(idx),
                             values=(row["Date"].strftime("%Y-%m-%d"), row["Category"],
                                     row["Description"], f"{row['Amount']:.2f}"))

        # summary cards
        s = dm.get_summary(df)
        self.card_vars["total"].set(f"Rs. {s['total']:,.2f}")
        self.card_vars["average"].set(f"Rs. {s['average']:,.2f}")
        self.card_vars["highest"].set(f"Rs. {s['highest']:,.2f}")
        self.card_vars["top_category"].set(s["top_category"])

        # charts
        draw_charts(self.fig, df, selected_month if monthly_view else None)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    ExpenseApp(root)
    root.mainloop()