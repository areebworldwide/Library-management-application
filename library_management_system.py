# library_animated_persistent.py
# Single-file animated Library Management System with JSON persistence
# Requires Python 3.x (Tkinter included)

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime, timedelta

# ---------- Persistence ----------
DATA_FILE = "library_data.json"

def make_empty_store():
    return {"books": {}, "users": [], "issued": []}

def load_store():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return make_empty_store()
    return make_empty_store()

def save_store():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Save error", f"Could not save data: {e}")

store = load_store()  # store: { books: {title: {author, qty, reserved:list}}, users: [name], issued: [txs] }

# ---------- Basic config + colors ----------
APP_BG = "#071229"
CARD_COLORS = ["#10b981", "#ef4444", "#3b82f6", "#8b5cf6", "#f59e0b", "#6366f1",
               "#ec4899", "#06b6d4", "#7c3aed", "#0891b2", "#16a34a", "#fb923c"]
TITLE_FONT = ("Inter", 22, "bold")
ENTRY_FONT = ("Inter", 13)

# ---------- Tk root ----------
root = tk.Tk()
root.title("Library — Persistent Animated UI")
root.geometry("1100x700")
root.minsize(900, 600)
root.configure(bg=APP_BG)

current_user = {"name": ""}

# Frames
welcome_frame = tk.Frame(root, bg=APP_BG)
dashboard_frame = tk.Frame(root, bg=APP_BG)
overlay_frame = tk.Frame(root, bg=APP_BG)  # slide-in overlay for full-screen forms
welcome_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# ---------- Animation helper ----------
def slide_widget(widget, start_rel_y, end_rel_y, steps=16, delay=16):
    # place widget with variable rely
    def step(i):
        frac = i / steps
        y = start_rel_y + (end_rel_y - start_rel_y) * frac
        widget.place(relx=0, rely=y, relwidth=1, relheight=1)
        if i < steps:
            widget.after(delay, lambda: step(i+1))
    step(0)

# ---------- Styled button helper ----------
def styled_button(parent, text, bg="#2b6cb0", command=None):
    b = tk.Button(parent, text=text, bg=bg, fg="white", font=("Inter", 11, "bold"),
                  bd=0, relief="flat", command=command)
    def on_enter(e):
        b.config(bg="#0ea5a4")
    def on_leave(e, color=bg):
        b.config(bg=color)
    b.bind("<Enter>", on_enter); b.bind("<Leave>", on_leave)
    return b

# ---------- Welcome Screen ----------
def build_welcome():
    for w in welcome_frame.winfo_children():
        w.destroy()
    # background blocks
    c = tk.Canvas(welcome_frame, highlightthickness=0, bg=APP_BG)
    c.place(relx=0, rely=0, relwidth=1, relheight=1)
    wwidth = root.winfo_width() or 1100
    wheight= root.winfo_height() or 700
    for i in range(0, 12):
        color = "#0b3a50" if i % 2 == 0 else APP_BG
        c.create_rectangle(0, i*(wheight/12), wwidth, (i+1)*(wheight/12), outline=color, fill=color)
    # card
    card = tk.Frame(welcome_frame, bg="white")
    card.place(relx=0.5, rely=0.45, anchor="center", width=640, height=320)
    tk.Label(card, text="Welcome to the Library", font=TITLE_FONT, bg="white", fg="#0b1220").pack(pady=(18,8))
    tk.Label(card, text="Enter your name to continue", font=("Inter", 11), bg="white", fg="#475569").pack(pady=(0,14))
    name_var = tk.StringVar()
    entry = tk.Entry(card, font=ENTRY_FONT, textvariable=name_var, justify="center", bd=1, relief="solid")
    entry.pack(ipady=10, ipadx=10, pady=8)
    entry.focus_set()
    def on_continue():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Please enter your name to continue.")
            return
        current_user["name"] = name
        # auto-register if new
        if name not in store.get("users", []):
            store.setdefault("users", []).append(name)
            save_store()
        slide_out_welcome_and_show_dashboard()
    btn = styled_button(card, "Continue", bg="#06b6d4", command=on_continue)
    btn.pack(pady=12, ipadx=8, ipady=6)
    tk.Label(card, text="Data saved to 'library_data.json' automatically.", font=("Inter", 9), bg="white", fg="#94a3b8").pack(side="bottom", pady=10)

def slide_out_welcome_and_show_dashboard():
    dashboard_frame.place(relx=0, rely=1, relwidth=1, relheight=1)
    build_dashboard()
    slide_widget(dashboard_frame, start_rel_y=1.0, end_rel_y=0.0, steps=16, delay=18)
    # hide welcome after small delay
    def hide():
        welcome_frame.place_forget()
    root.after(350, hide)

# ---------- Overlay form helper ----------
def show_overlay_form(title, fields, submit_callback, initial_values=None):
    """
    fields: list of tuples (label, key, type) where type in {'str','int','days'} (type optional)
    submit_callback receives dict key->value
    """
    for w in overlay_frame.winfo_children():
        w.destroy()
    overlay_frame.place(relx=0, rely=1, relwidth=1, relheight=1)
    overlay_frame.configure(bg="#071029")
    card = tk.Frame(overlay_frame, bg="#0b1220")
    card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)
    tk.Label(card, text=title, font=TITLE_FONT, bg="#0b1220", fg="white").pack(pady=(18,10))
    form_area = tk.Frame(card, bg="#0b1220")
    form_area.pack(expand=True, fill="both", padx=24, pady=6)
    entries = {}
    for field in fields:
        label, key = field[0], field[1]
        typ = field[2] if len(field) > 2 else 'str'
        row = tk.Frame(form_area, bg="#0b1220")
        row.pack(fill="x", pady=8)
        tk.Label(row, text=label, bg="#0b1220", fg="#cbd5e1", font=("Inter", 11)).pack(side="left", padx=(4,12))
        ent = tk.Entry(row, font=ENTRY_FONT, width=36, bd=0, relief="solid")
        ent.pack(side="left", padx=6)
        if initial_values and key in initial_values:
            ent.insert(0, str(initial_values[key]))
        entries[key] = (ent, typ)
    ctrl = tk.Frame(card, bg="#0b1220")
    ctrl.pack(pady=10)
    def on_submit():
        vals = {}
        for k, (ent, typ) in entries.items():
            v = ent.get().strip()
            if typ in ('int','days'):
                try:
                    vals[k] = int(v)
                except:
                    messagebox.showerror("Invalid", f"Field '{k}' needs a number.")
                    return
            else:
                vals[k] = v
        submit_callback(vals)
        slide_out_overlay()
    styled_button(ctrl, "Submit", bg="#06b6d4", command=on_submit).pack(side="left", padx=12)
    styled_button(ctrl, "Cancel", bg="#ef4444", command=slide_out_overlay).pack(side="left", padx=12)
    slide_widget(overlay_frame, start_rel_y=1.0, end_rel_y=0.0, steps=16, delay=16)

def slide_out_overlay():
    slide_widget(overlay_frame, start_rel_y=0.0, end_rel_y=1.0, steps=16, delay=16)
    def hide():
        overlay_frame.place_forget()
    overlay_frame.after(350, hide)

# ---------- Feature implementations (all 12) ----------
def add_book_action(vals):
    title = vals.get("title","").strip()
    author = vals.get("author","").strip() or "Unknown"
    qty = vals.get("qty",0)
    if not title:
        messagebox.showerror("Validation", "Title required.")
        return
    store.setdefault("books", {})
    store["books"].setdefault(title, {"author": author, "qty":0, "reserved":[]})
    store["books"][title]["qty"] += int(qty)
    save_store()
    messagebox.showinfo("Added", f"'{title}' added ({qty}).")

def add_book():
    fields = [("Title", "title"), ("Author", "author"), ("Quantity", "qty", "int")]
    show_overlay_form("Add Book", fields, add_book_action)

def remove_book_action(vals):
    title = vals.get("title","").strip()
    if not title or title not in store.get("books", {}):
        messagebox.showerror("Error", "Book not found.")
        return
    # prevent if issued
    for tx in store.get("issued", []):
        if tx["book"] == title and not tx.get("returned", False):
            messagebox.showerror("Error", "Book currently issued; cannot remove.")
            return
    del store["books"][title]
    save_store()
    messagebox.showinfo("Removed", f"'{title}' removed.")

def remove_book():
    show_overlay_form("Remove Book", [("Title", "title")], remove_book_action)

def update_book_action(vals):
    title = vals.get("title","").strip()
    if title not in store.get("books", {}):
        messagebox.showerror("Error", "Book not found.")
        return
    author = vals.get("author","").strip() or store["books"][title]["author"]
    qty = vals.get("qty", store["books"][title]["qty"])
    store["books"][title]["author"] = author
    store["books"][title]["qty"] = int(qty)
    save_store()
    messagebox.showinfo("Updated", f"'{title}' updated.")

def update_book():
    fields = [("Title", "title"), ("New Author", "author"), ("New Quantity", "qty", "int")]
    show_overlay_form("Update Book", fields, update_book_action)

def search_book_action(vals):
    q = vals.get("q","").strip().lower()
    if not q:
        messagebox.showerror("Error", "Enter search query.")
        return
    lines = []
    for t,d in store.get("books", {}).items():
        if q in t.lower() or q in d.get("author","").lower():
            lines.append(f"{t} — {d.get('author','')} | Qty: {d.get('qty',0)}")
    if not lines:
        messagebox.showinfo("No results", "No books match.")
        return
    # show result overlay
    for w in overlay_frame.winfo_children():
        w.destroy()
    overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay_frame, bg="#0b1220"); card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)
    tk.Label(card, text="Search Results", font=TITLE_FONT, bg="#0b1220", fg="white").pack(pady=12)
    txt = tk.Text(card, bg="#071029", fg="white"); txt.pack(expand=True, fill="both", padx=12, pady=12)
    txt.insert("1.0", "\n".join(lines)); txt.configure(state="disabled")
    styled_button(card, "Close", bg="#ef4444", command=slide_out_overlay).pack(pady=8)

def search_book():
    show_overlay_form("Search Book", [("Search (title/author)", "q")], search_book_action)

def list_all_books():
    books = store.get("books", {})
    if not books:
        messagebox.showinfo("All Books", "No books available.")
        return
    lines = []
    for t,d in books.items():
        reserved = f" | Reserved: {', '.join(d.get('reserved',[]))}" if d.get("reserved") else ""
        lines.append(f"{t} — {d.get('author','')} | Qty: {d.get('qty',0)}{reserved}")
    # show overlay list
    for w in overlay_frame.winfo_children():
        w.destroy()
    overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay_frame, bg="#0b1220"); card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)
    tk.Label(card, text="All Books", font=TITLE_FONT, bg="#0b1220", fg="white").pack(pady=12)
    txt = tk.Text(card, bg="#071029", fg="white"); txt.pack(expand=True, fill="both", padx=12, pady=12)
    txt.insert("1.0", "\n".join(lines)); txt.configure(state="disabled")
    styled_button(card, "Close", bg="#ef4444", command=slide_out_overlay).pack(pady=8)

# Users
def register_user_action(vals):
    name = vals.get("name","").strip()
    if not name:
        messagebox.showerror("Error", "Name required.")
        return
    if name in store.get("users", []):
        messagebox.showerror("Error", "User exists.")
        return
    store.setdefault("users", []).append(name)
    save_store()
    messagebox.showinfo("Registered", f"'{name}' registered.")

def register_user():
    show_overlay_form("Register User", [("Name", "name")], register_user_action)

def delete_user_action(vals):
    name = vals.get("name","").strip()
    if name not in store.get("users", []):
        messagebox.showerror("Error", "User not found.")
        return
    for tx in store.get("issued", []):
        if tx["user"] == name and not tx.get("returned", False):
            messagebox.showerror("Error", "User has issued books; can't delete.")
            return
    store["users"].remove(name)
    # also remove reservations
    for d in store.get("books", {}).values():
        if "reserved" in d:
            d["reserved"] = [r for r in d.get("reserved",[]) if r != name]
    save_store()
    messagebox.showinfo("Deleted", f"'{name}' removed.")

def delete_user():
    show_overlay_form("Delete User", [("Name", "name")], delete_user_action)

def update_user_action(vals):
    old = vals.get("old","").strip()
    new = vals.get("new","").strip()
    if old not in store.get("users", []):
        messagebox.showerror("Error", "User not found.")
        return
    if not new:
        messagebox.showerror("Error", "New name required.")
        return
    idx = store["users"].index(old)
    store["users"][idx] = new
    # update issued and reserved
    for tx in store.get("issued", []):
        if tx["user"] == old:
            tx["user"] = new
    for d in store.get("books", {}).values():
        if "reserved" in d:
            d["reserved"] = [new if x==old else x for x in d.get("reserved",[])]
    save_store()
    messagebox.showinfo("Updated", f"'{old}' -> '{new}'")

def update_user():
    show_overlay_form("Update User", [("Old Name","old"), ("New Name","new")], update_user_action)

def list_users():
    users = store.get("users", [])
    lines = users[:] if users else ["(No users)"]
    for w in overlay_frame.winfo_children():
        w.destroy()
    overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay_frame, bg="#0b1220"); card.place(relx=0.5, rely=0.5, anchor="center", width=700, height=500)
    tk.Label(card, text="Registered Users", font=TITLE_FONT, bg="#0b1220", fg="white").pack(pady=12)
    txt = tk.Text(card, bg="#071029", fg="white")
    txt.insert("1.0", "\n".join(lines))
    txt.configure(state="disabled")
    txt.pack(expand=True, fill="both", padx=12, pady=12)
    styled_button(card, "Close", bg="#ef4444", command=slide_out_overlay).pack(pady=8)

# Issue / Return / Reserve
def issue_book_action(vals):
    user = vals.get("user","").strip()
    book = vals.get("book","").strip()
    days = vals.get("days", 14)
    if user not in store.get("users", []):
        messagebox.showerror("Error", "User not registered.")
        return
    if book not in store.get("books", {}):
        messagebox.showerror("Error", "Book not found.")
        return
    if store["books"][book].get("qty",0) <= 0:
        messagebox.showerror("Unavailable", "No copies available.")
        return
    store["books"][book]["qty"] -= 1
    tx = {"user": user, "book": book,
          "issued_on": datetime.now().isoformat(),
          "due_date": (datetime.now() + timedelta(days=int(days))).isoformat(),
          "returned": False}
    store.setdefault("issued", []).append(tx)
    save_store()
    messagebox.showinfo("Issued", f"'{book}' issued to {user} for {days} days.")

def issue_book():
    fields = [("User Name","user"), ("Book Title","book"), ("Days","days","days")]
    show_overlay_form("Issue Book", fields, issue_book_action)

def return_book_action(vals):
    user = vals.get("user","").strip()
    book = vals.get("book","").strip()
    for tx in reversed(store.get("issued", [])):
        if tx["user"] == user and tx["book"] == book and not tx.get("returned", False):
            tx["returned"] = True
            tx["returned_on"] = datetime.now().isoformat()
            store["books"][book]["qty"] = store["books"].get(book, {}).get("qty", 0) + 1
            save_store()
            messagebox.showinfo("Returned", f"'{book}' returned by {user}.")
            return
    messagebox.showerror("Error", "No matching issued record found.")

def return_book():
    fields = [("User Name","user"), ("Book Title","book")]
    show_overlay_form("Return Book", fields, return_book_action)

def reserve_book_action(vals):
    user = vals.get("user","").strip()
    book = vals.get("book","").strip()
    if user not in store.get("users", []):
        messagebox.showerror("Error", "User not found.")
        return
    if book not in store.get("books", {}):
        messagebox.showerror("Error", "Book not found.")
        return
    store["books"][book].setdefault("reserved", []).append(user)
    save_store()
    messagebox.showinfo("Reserved", f"'{book}' reserved for {user}.")

def reserve_book():
    fields = [("User Name","user"), ("Book Title","book")]
    show_overlay_form("Reserve Book", fields, reserve_book_action)

def list_issued_books_ui():
    lines = []
    for tx in store.get("issued", []):
        if not tx.get("returned", False):
            lines.append(f"{tx['book']} → {tx['user']} | Issued: {tx['issued_on'][:19]} | Due: {tx['due_date'][:10]}")
    if not lines:
        messagebox.showinfo("Issued Books", "No books currently issued.")
        return
    for w in overlay_frame.winfo_children():
        w.destroy()
    overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay_frame, bg="#0b1220"); card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)
    tk.Label(card, text="Issued Books", font=TITLE_FONT, bg="#0b1220", fg="white").pack(pady=12)
    txt = tk.Text(card, bg="#071029", fg="white"); txt.pack(expand=True, fill="both", padx=12, pady=12)
    txt.insert("1.0", "\n".join(lines)); txt.configure(state="disabled")
    styled_button(card, "Close", bg="#ef4444", command=slide_out_overlay).pack(pady=8)

# ---------- Dashboard builder (3x4 grid) ----------
def styled_card(parent, text, color, command):
    card = tk.Frame(parent, bg=color, bd=0, relief="flat")
    lbl  = tk.Label(card, text=text, bg=color, fg="white", font=("Inter", 13, "bold"))
    lbl.pack(expand=True, fill="both", padx=12, pady=12)
    def on_enter(e):
        card.configure(bg="#041227"); lbl.configure(bg="#041227")
    def on_leave(e, col=color):
        card.configure(bg=col); lbl.configure(bg=col)
    card.bind("<Enter>", on_enter); card.bind("<Leave>", on_leave)
    lbl.bind("<Enter>", on_enter); lbl.bind("<Leave>", on_leave)
    card.bind("<Button-1>", lambda e: command())
    lbl.bind("<Button-1>", lambda e: command())
    return card

def build_dashboard():
    for w in dashboard_frame.winfo_children():
        w.destroy()
    dashboard_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    top = tk.Frame(dashboard_frame, bg="#071229", height=70)
    top.pack(fill="x")
    tk.Label(top, text=f"Welcome, {current_user['name']}", bg="#071229", fg="white", font=("Inter", 16, "bold")).pack(side="left", padx=20)
    tk.Label(top, text="Click a card to open a full-screen form", bg="#071229", fg="#94a3b8", font=("Inter", 10)).pack(side="left", padx=8)
    main = tk.Frame(dashboard_frame, bg="#071029")
    main.pack(expand=True, fill="both", padx=36, pady=20)
    features = [
        ("Add Book", add_book, CARD_COLORS[0]),
        ("Remove Book", remove_book, CARD_COLORS[1]),
        ("Update Book", update_book, CARD_COLORS[2]),
        ("Search Book", search_book, CARD_COLORS[3]),
        ("List All Books", list_all_books, CARD_COLORS[4]),
        ("Register User", register_user, CARD_COLORS[5]),
        ("Delete User", delete_user, CARD_COLORS[6]),
        ("Update User", update_user, CARD_COLORS[7]),
        ("List Users", list_users, CARD_COLORS[8]),
        ("Issue Book", issue_book, CARD_COLORS[9]),
        ("Return Book", return_book, CARD_COLORS[10]),
        ("Reserve Book", reserve_book, CARD_COLORS[11])
    ]
    cols = 3
    for i, (label, cmd, color) in enumerate(features[:12]):
        r, c = divmod(i, cols)
        card = styled_card(main, label, color, cmd)
        card.grid(row=r, column=c, padx=18, pady=18, sticky="nsew")
        main.grid_columnconfigure(c, weight=1)
    rows_needed = (12 + cols - 1)//cols
    for rr in range(rows_needed):
        main.grid_rowconfigure(rr, weight=1)

# ---------- Start ----------
build_welcome()
root.bind("<Escape>", lambda e: slide_out_overlay() if overlay_frame.winfo_ismapped() else None)
root.mainloop()
