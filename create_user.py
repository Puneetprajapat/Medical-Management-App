import tkinter as tk
from tkinter import ttk, messagebox
from src.database import Database

class CreateUserWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Create New User")
        self.root.geometry("400x400")
        
        # Create form fields
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username = tk.Entry(self.root)
        self.username.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password = tk.Entry(self.root, show="*")
        self.password.pack(pady=5)
        
        tk.Label(self.root, text="Email:").pack(pady=5)
        self.email = tk.Entry(self.root)
        self.email.pack(pady=5)
        
        tk.Label(self.root, text="Full Name:").pack(pady=5)
        self.full_name = tk.Entry(self.root)
        self.full_name.pack(pady=5)
        
        tk.Label(self.root, text="User Type:").pack(pady=5)
        self.user_type = ttk.Combobox(self.root, values=["patient", "doctor", "admin"])
        self.user_type.set("patient")
        self.user_type.pack(pady=5)
        
        # Create submit button
        tk.Button(self.root, text="Create User", command=self.create_user).pack(pady=20)
        
    def create_user(self):
        try:
            db = Database()
            db.add_user(
                username=self.username.get(),
                password=self.password.get(),
                email=self.email.get(),
                full_name=self.full_name.get(),
                user_type=self.user_type.get()
            )
            messagebox.showinfo("Success", "User created successfully!")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = CreateUserWindow()
    app.root.mainloop()