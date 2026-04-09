import tkinter as tk
from tkinter import ttk, messagebox
import struct
import os
import sys

class MiniDBEngine:
    def __init__(self, db_name="my_database.db"):
        # Place DB in the same folder as the EXE
        self.db_path = os.path.join(os.path.dirname(sys.argv[0]), db_name)
        self.record_format = "I32s64s"
        self.record_size = struct.calcsize(self.record_format)

    def create_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "wb") as f:
                pass # Create empty file

    def insert(self, user_id, name, email):
        binary_data = struct.pack(
            self.record_format, 
            int(user_id), 
            name.encode('utf-8')[:32], 
            email.encode('utf-8')[:64]
        )
        with open(self.db_path, "ab") as f:
            f.write(binary_data)

    def select_all(self):
        rows = []
        if not os.path.exists(self.db_path): return rows
        with open(self.db_path, "rb") as f:
            while True:
                data = f.read(self.record_size)
                if not data: break
                res = struct.unpack(self.record_format, data)
                rows.append((res[0], res[1].decode('utf-8').strip('\x00'), res[2].decode('utf-8').strip('\x00')))
        return rows

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniDB Studio Pro")
        self.root.geometry("700x500")
        self.engine = None
        
        # Style
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Start with the Wizard
        self.show_wizard()

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- SCREEN 1: WIZARD ---
    def show_wizard(self):
        self.clear_screen()
        wizard_frame = tk.Frame(self.main_container, pady=50)
        wizard_frame.pack()

        ttk.Label(wizard_frame, text="Welcome to MiniDB Wizard", style="Header.TLabel").pack(pady=10)
        ttk.Label(wizard_frame, text="This tool will create a new high-performance\nbinary database on your computer.").pack(pady=5)
        
        ttk.Label(wizard_frame, text="Database Name:").pack(pady=(20, 0))
        self.db_name_entry = ttk.Entry(wizard_frame, width=30)
        self.db_name_entry.insert(0, "storage.db")
        self.db_name_entry.pack(pady=5)

        btn = ttk.Button(wizard_frame, text="Create & Open Database", command=self.finish_wizard)
        btn.pack(pady=20)

    def finish_wizard(self):
        name = self.db_name_entry.get()
        if not name.endswith(".db"): name += ".db"
        self.engine = MiniDBEngine(name)
        self.engine.create_db()
        self.show_main_ui()

    # --- SCREEN 2: MAIN DASHBOARD ---
    def show_main_ui(self):
        self.clear_screen()
        
        # Sidebar / Top form
        form_frame = tk.LabelFrame(self.main_container, text=" Add New Record ", padx=10, pady=10)
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Input Fields
        tk.Label(form_frame, text="ID:").grid(row=0, column=0, padx=5)
        self.ent_id = ttk.Entry(form_frame, width=10)
        self.ent_id.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5)
        self.ent_name = ttk.Entry(form_frame, width=20)
        self.ent_name.grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Email:").grid(row=0, column=4, padx=5)
        self.ent_email = ttk.Entry(form_frame, width=25)
        self.ent_email.grid(row=0, column=5, padx=5)

        btn_add = ttk.Button(form_frame, text="Save Record", command=self.add_data)
        btn_add.grid(row=0, column=6, padx=10)

        # Data View
        self.tree = ttk.Treeview(self.main_container, columns=("ID", "Name", "Email"), show='headings')
        self.tree.heading("ID", text="User ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Email", text="Email Address")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Footer
        footer = tk.Frame(self.main_container, bg="#f0f0f0")
        footer.pack(fill="x", side="bottom")
        self.lbl_status = tk.Label(footer, text=f"DB: {self.engine.db_path}", font=("Segoe UI", 8))
        self.lbl_status.pack(side="left", padx=5)

        self.refresh_grid()

    def add_data(self):
        try:
            self.engine.insert(self.ent_id.get(), self.ent_name.get(), self.ent_email.get())
            self.ent_id.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.ent_email.delete(0, tk.END)
            self.refresh_grid()
            messagebox.showinfo("Success", "Data saved to binary storage!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")

    def refresh_grid(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in self.engine.select_all(): self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
