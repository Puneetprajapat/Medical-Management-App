import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

from src.database import Database
from src.ui.admin import AdminApp
from src.ui.patient import PatientApp

db = Database()

class HomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Management System")
        self.root.geometry("800x600")
        
        # Main content frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Login variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Create the home screen
        self.create_home_screen()
        
    def create_home_screen(self):
        # Clear any existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(
            header_frame, 
            text="Medical Management System",
            font=("Arial", 24, "bold")
        ).pack(side=tk.LEFT)
        
        # Create content area with two panels
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Login
        login_frame = ttk.LabelFrame(content_frame, text="Login", padding=(20, 10))
        login_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(login_frame, text="Username:").pack(anchor=tk.W, pady=(10, 5))
        ttk.Entry(login_frame, textvariable=self.username_var, width=30).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Password:").pack(anchor=tk.W, pady=(5, 5))
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(login_frame, text="Login", command=self.login).pack(pady=(10, 0))
        
        # Right panel - Quick access
        access_frame = ttk.LabelFrame(content_frame, text="Quick Access", padding=(20, 10))
        access_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(
            access_frame, 
            text="Select a role for demo access:",
            font=("Arial", 12)
        ).pack(anchor=tk.W, pady=(10, 20))
        
        ttk.Button(
            access_frame, 
            text="Admin Access",
            command=self.open_admin_interface
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            access_frame, 
            text="Patient Access",
            command=self.open_patient_interface
        ).pack(fill=tk.X, pady=5)
        
        # Footer
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(
            footer_frame, 
            text="© 2025 Medical Management System",
            font=("Arial", 8)
        ).pack(side=tk.RIGHT)
    
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        user = db.get_user(username)
        
        if not user or user["password"] != password:
            messagebox.showerror("Error", "Invalid username or password")
            return
        
        # Successful login
        self.open_interface_for_user(user)
    
    def open_interface_for_user(self, user):
        if user["user_type"] == "admin":
            self.open_admin_interface()
        elif user["user_type"] == "patient":
            self.open_patient_interface(user["id"])
        elif user["user_type"] == "doctor":
            # Future implementation
            messagebox.showinfo("Doctor Interface", "Doctor interface coming soon!")
        else:
            messagebox.showerror("Error", "Unknown user type")
    
    def open_admin_interface(self):
        self.root.withdraw()  # Hide main window
        admin_window = tk.Toplevel(self.root)
        app = AdminApp(admin_window, self)
        
    def open_patient_interface(self, user_id=None):
        self.root.withdraw()  # Hide main window
        patient_window = tk.Toplevel(self.root)
        app = PatientApp(patient_window, user_id, self)
    
    def show(self):
        self.root.deiconify()  # Show the main window again