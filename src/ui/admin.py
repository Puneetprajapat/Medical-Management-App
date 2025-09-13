import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from tkcalendar import DateEntry

from src.database import Database

db = Database()


class AdminApp:
    def __init__(self, root, parent_app=None):
        self.root = root
        self.parent_app = parent_app
        self.root.title("Medicine Management System - Admin")
        self.root.geometry("900x600")

        self.name_var = tk.StringVar()
        self.details_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.stocked_on_var = tk.StringVar(value=str(date.today()))
        self.expires_on_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.batch_no_var = tk.StringVar()
        self.storage_var = tk.StringVar()
        self.prescription_var = tk.BooleanVar()
        self.selected_medicine_var = tk.StringVar()

        self.main_frame = ttk.Frame(self.root)
        self.form_frame = ttk.Frame(self.root)

        self.create_header()
        self.show_main_page()
    
    def create_header(self):
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Title
        ttk.Label(header, text="Medicine Management System - Admin", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Navigation
        nav_frame = ttk.Frame(header)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="Back to Home", command=self.go_back_to_home).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def go_back_to_home(self):
        if self.parent_app:
            self.parent_app.show()
            self.root.withdraw()
        else:
            messagebox.showinfo("Information", "No parent app to return to")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()

    def show_main_page(self):
        self.form_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame, text="Medicine Inventory", font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)

        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Add Medicine", command=self.show_form_page).pack(
            side=tk.LEFT, padx=5
        )

        self.remove_frame = ttk.Frame(button_frame)
        self.remove_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.remove_frame, text="Remove Medicine", command=self.show_remove_dropdown
        ).pack(side=tk.LEFT)

        columns = ("id", "name", "quantity", "manufacturer", "expires_on")
        self.medicine_tree = ttk.Treeview(
            self.main_frame, columns=columns, show="headings"
        )

        self.medicine_tree.heading("id", text="ID")
        self.medicine_tree.heading("name", text="Name")
        self.medicine_tree.heading("quantity", text="Quantity")
        self.medicine_tree.heading("manufacturer", text="Manufacturer")
        self.medicine_tree.heading("expires_on", text="Expires On")

        self.medicine_tree.column("id", width=50)
        self.medicine_tree.column("name", width=200)
        self.medicine_tree.column("quantity", width=100)
        self.medicine_tree.column("manufacturer", width=150)
        self.medicine_tree.column("expires_on", width=100)

        scrollbar = ttk.Scrollbar(
            self.main_frame, orient=tk.VERTICAL, command=self.medicine_tree.yview
        )
        self.medicine_tree.configure(yscroll=scrollbar.set)

        self.medicine_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_medicines()

    def show_remove_dropdown(self):
        medicines = db.get_all_medicines()

        if not medicines:
            messagebox.showinfo("No Medicines", "There are no medicines to remove.")
            return

        self.popup = tk.Toplevel(self.root)
        self.popup.title("Remove Medicine")
        self.popup.geometry("400x150")
        self.popup.transient(self.root)
        self.popup.grab_set()

        self.popup.update_idletasks()
        width = self.popup.winfo_width()
        height = self.popup.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        self.popup.geometry(f"+{x}+{y}")

        ttk.Label(
            self.popup, text="Select Medicine to Remove:", font=("Arial", 12)
        ).pack(pady=10)

        self.medicine_map = {
            f"{m['id']} - {m['name']}": (m["id"], m["name"]) for m in medicines
        }
        self.selected_medicine_var.set("")

        medicine_dropdown = ttk.Combobox(
            self.popup, textvariable=self.selected_medicine_var, width=40
        )
        medicine_dropdown["values"] = list(self.medicine_map.keys())
        medicine_dropdown.pack(pady=5)

        button_frame = ttk.Frame(self.popup)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame, text="Remove", command=self.confirm_remove_medicine
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.popup.destroy).pack(
            side=tk.LEFT, padx=10
        )

    def confirm_remove_medicine(self):
        selected = self.selected_medicine_var.get()

        if not selected:
            messagebox.showwarning(
                "Selection Required", "Please select a medicine to remove."
            )
            return

        medicine_id, medicine_name = self.medicine_map[selected]

        self.popup.destroy()

        confirm = messagebox.askyesno(
            "Confirm Deletion", f"Are you sure you want to delete '{medicine_name}'?"
        )

        if confirm:
            try:
                db.remove_medicine(medicine_id)
                messagebox.showinfo(
                    "Success", f"Medicine '{medicine_name}' removed successfully"
                )

                self.load_medicines()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove medicine: {str(e)}")

    def load_medicines(self):
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        medicines = db.get_all_medicines()

        for medicine in medicines:
            self.medicine_tree.insert(
                "",
                tk.END,
                values=(
                    medicine["id"],
                    medicine["name"],
                    medicine["quantity"],
                    medicine["manufacturer"],
                    medicine["expires_on"],
                ),
            )

    def show_form_page(self):
        self.main_frame.pack_forget()
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for widget in self.form_frame.winfo_children():
            widget.destroy()

        self.name_var.set("")
        self.details_var.set("")
        self.quantity_var.set("")
        self.manufacturer_var.set("")
        self.batch_no_var.set("")
        self.storage_var.set("")
        self.prescription_var.set(False)

        header_frame = ttk.Frame(self.form_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Button(header_frame, text="← Back", command=self.show_main_page).pack(
            side=tk.LEFT
        )
        ttk.Label(
            header_frame, text="Add New Medicine", font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT, padx=20)

        # Regular text entry fields
        text_fields = [
            ("Name", self.name_var),
            ("Details", self.details_var),
            ("Quantity", self.quantity_var),
            ("Manufacturer", self.manufacturer_var),
            ("Batch Number", self.batch_no_var),
            ("Storage Instructions", self.storage_var),
        ]

        row = 1
        for label_text, var in text_fields:
            ttk.Label(self.form_frame, text=label_text).grid(
                row=row, column=0, padx=10, pady=5, sticky="e"
            )
            ttk.Entry(self.form_frame, textvariable=var, width=30).grid(
                row=row, column=1, padx=10, pady=5, sticky="w"
            )
            row += 1

        # Calendar widgets for date fields
        ttk.Label(self.form_frame, text="Stocked On").grid(
            row=row, column=0, padx=10, pady=5, sticky="e"
        )
        self.stocked_on_cal = DateEntry(
            self.form_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd",
            firstweekday="sunday",
        )
        self.stocked_on_cal.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1

        ttk.Label(self.form_frame, text="Expires On").grid(
            row=row, column=0, padx=10, pady=5, sticky="e"
        )
        self.expires_on_cal = DateEntry(
            self.form_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd",
            firstweekday="sunday",
        )
        self.expires_on_cal.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1

        ttk.Checkbutton(
            self.form_frame,
            text="Prescription Required",
            variable=self.prescription_var,
        ).grid(row=row, columnspan=2, pady=5)
        row += 1

        ttk.Button(self.form_frame, text="Submit", command=self.submit_form).grid(
            row=row, columnspan=2, pady=10
        )

    def submit_form(self):
        try:
            data = {
                "Name": self.name_var.get(),
                "Details": self.details_var.get(),
                "Quantity": self.quantity_var.get(),
                "Stocked On": self.stocked_on_cal.get_date().strftime("%Y-%m-%d"),
                "Expires On": self.expires_on_cal.get_date().strftime("%Y-%m-%d"),
                "Manufacturer": self.manufacturer_var.get(),
                "Batch Number": self.batch_no_var.get(),
                "Storage Instructions": self.storage_var.get(),
                "Prescription Required": self.prescription_var.get(),
            }

            if not data["Name"] or not data["Quantity"]:
                messagebox.showerror("Error", "Name and Quantity are required fields")
                return

            db.add_medicine(
                name=data["Name"],
                details=data["Details"],
                quantity=int(data["Quantity"]),
                stocked_on=data["Stocked On"],
                expires_on=data["Expires On"],
                manufacturer=data["Manufacturer"],
                batch_no=data["Batch Number"],
                storage=data["Storage Instructions"],
                prescription=data["Prescription Required"],
            )
            messagebox.showinfo(
                "Success", f"Medicine '{data['Name']}' added successfully"
            )
            self.show_main_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")