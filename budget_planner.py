import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import csv
import os
from datetime import datetime

FILE_NAME = "expenses.csv"
CATEGORIES_FILE = "categories.txt"
budget = 0  # default budget
# Default budget planner categories
DEFAULT_CATEGORIES = [
    "Food & Groceries",
    "Travel & Transport",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Health & Medical",
    "Education",
    "Savings & Investments",
    "Gifts & Donations",
    "Miscellaneous"
]

# Load categories from file
def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as f:
            cats = [line.strip() for line in f if line.strip()]
            if cats:
                return cats
    return DEFAULT_CATEGORIES.copy()

# Save categories to file
def save_categories():
    with open(CATEGORIES_FILE, "w") as f:
        for cat in categories:
            f.write(cat + "\n")

# Ensure CSV file exists
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as file:
        pass

categories = load_categories()

# Add new category
def add_category():
    global categories
    new_cat = simpledialog.askstring("Add Category", "Enter new category:")
    if new_cat and new_cat.strip():
        new_cat = new_cat.strip()
        if new_cat not in categories:
            categories.append(new_cat)
            save_categories()
            update_category_menu()
            messagebox.showinfo("Added", f"Category '{new_cat}' added!")
        else:
            messagebox.showwarning("Exists", "Category already exists!")

# Update dropdown menu
def update_category_menu():
    category_menu["values"] = categories
    category_var.set(categories[0])

# Save expense to CSV
def save_expense():
    amount = amount_entry.get().strip()
    category = category_var.get().strip()
    note = note_entry.get().strip()

    if not amount or not category:
        messagebox.showerror("Error", "Please fill amount and category!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return

    date = datetime.now().strftime("%Y-%m-%d")

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([amount, category, note, date])

    amount_entry.delete(0, tk.END)
    category_var.set(categories[0])
    note_entry.delete(0, tk.END)
    load_expenses()

# Load expenses from CSV
def load_expenses():
    expenses_list.delete(0, tk.END)
    total = 0
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 4 and row[0].strip():
                    try:
                        total += float(row[0])
                        expenses_list.insert(
                            tk.END, f"₹{row[0]} - {row[1]} ({row[2]}) [{row[3]}]"
                        )
                    except ValueError:
                        pass
    total_label.config(text=f"Total: ₹{total:.2f}")
    remaining = budget - total if budget else 0
    budget_label.config(text=f"Budget: ₹{budget} | Remaining: ₹{remaining:.2f}")

# Delete selected expense
def delete_expense():
    selected = expenses_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select an expense to delete!")
        return

    index = selected[0]
    expenses = []

    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        expenses = [row for row in reader if row]

    if 0 <= index < len(expenses):
        expenses.pop(index)

    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(expenses)

    load_expenses()

# Edit selected expense
def edit_expense():
    selected = expenses_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select an expense to edit!")
        return

    index = selected[0]
    with open(FILE_NAME, "r") as file:
        expenses = [row for row in csv.reader(file) if row]

    if index >= len(expenses):
        return

    try:
        amount = simpledialog.askstring("Edit", "Enter new amount:", initialvalue=expenses[index][0])
        if amount is None:
            return
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return

    category = simpledialog.askstring("Edit", "Enter new category:", initialvalue=expenses[index][1])
    if not category:
        category = expenses[index][1]

    note = simpledialog.askstring("Edit", "Enter new note:", initialvalue=expenses[index][2])
    if note is None:
        note = expenses[index][2]

    expenses[index] = [amount, category, note, datetime.now().strftime("%Y-%m-%d")]

    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(expenses)

    load_expenses()

# Set budget
def set_budget():
    global budget
    value = simpledialog.askstring("Set Budget", "Enter your monthly budget:")
    if value:
        try:
            budget = float(value)
        except ValueError:
            messagebox.showerror("Error", "Budget must be a number!")
    load_expenses()

# Tkinter UI
root = tk.Tk()
root.title("Budget Planner - Expense Tracker")
root.geometry("420x560")

# Input fields
tk.Label(root, text="Amount (₹):").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

tk.Label(root, text="Category:").pack()
category_var = tk.StringVar()
category_menu = ttk.Combobox(root, textvariable=category_var, values=categories, state="readonly")
category_menu.pack(pady=2)

tk.Button(root, text="Add Category", command=add_category, bg="lightyellow").pack(pady=3)

tk.Label(root, text="Note:").pack()
note_entry = tk.Entry(root)
note_entry.pack()

tk.Button(root, text="Add Expense", command=save_expense, bg="lightgreen").pack(pady=5)

# Expense list
expenses_list = tk.Listbox(root, width=50, height=10)
expenses_list.pack(pady=10)

# Buttons
tk.Button(root, text="Delete Selected", command=delete_expense, bg="tomato").pack(pady=3)
tk.Button(root, text="Edit Selected", command=edit_expense, bg="lightblue").pack(pady=3)
tk.Button(root, text="Set Budget", command=set_budget, bg="orange").pack(pady=3)

# Labels
total_label = tk.Label(root, text="Total: ₹0", font=("Arial", 12, "bold"))
total_label.pack(pady=5)

budget_label = tk.Label(root, text="Budget: ₹0 | Remaining: ₹0", font=("Arial", 10))
budget_label.pack()

update_category_menu()
load_expenses()
root.mainloop()
