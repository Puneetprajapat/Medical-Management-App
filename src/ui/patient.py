import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
from tkcalendar import DateEntry
import os
import subprocess
import platform

from src.database import Database

db = Database()

class PatientApp:
    def __init__(self, root, user_id=None, parent_app=None):
        self.root = root
        self.user_id = user_id
        self.parent_app = parent_app
        self.root.title("Medicine Management System - Patient")
        self.root.geometry("900x600")
        
        # Get user data
        self.user = self.get_user_data()
        
        # Create frames
        self.dashboard_frame = ttk.Frame(self.root)
        self.schedules_frame = ttk.Frame(self.root)
        self.prescriptions_frame = ttk.Frame(self.root)
        
        # Create the UI
        self.create_header()
        self.create_sidebar()
        self.show_dashboard()
    
    def get_user_data(self):
        if not self.user_id:
            # For demo purposes, use the first patient in the database
            user = db.get_user("patient1")
            self.user_id = user["id"]
            return user
        return db.get_user_by_id(self.user_id)
    
    def create_header(self):
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Title
        ttk.Label(header, text="Medicine Management System - Patient", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Navigation
        nav_frame = ttk.Frame(header)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="Back to Home", command=self.go_back_to_home).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def create_sidebar(self):
        # Create main container for sidebar and content
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        sidebar = ttk.Frame(main_container, width=200, style="Sidebar.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)  # Don't shrink
        
        # Add user info
        user_frame = ttk.Frame(sidebar)
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(user_frame, text=f"Welcome,", font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(user_frame, text=self.user["full_name"], font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # Menu items
        menu_items = [
            ("Dashboard", self.show_dashboard),
            ("Medicine Schedules", self.show_schedules),
            ("Prescriptions", self.show_prescriptions)
        ]
        
        for text, command in menu_items:
            btn = ttk.Button(sidebar, text=text, command=command, width=18)
            btn.pack(pady=5, padx=10, fill=tk.X)
        
        # Content frame - will hold dashboard, schedules, and prescriptions frames
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Pack all content frames into the content_frame
        for frame in [self.dashboard_frame, self.schedules_frame, self.prescriptions_frame]:
            frame.pack(fill=tk.BOTH, expand=True)
    
    def hide_all_frames(self):
        for frame in [self.dashboard_frame, self.schedules_frame, self.prescriptions_frame]:
            frame.pack_forget()
    
    def show_dashboard(self):
        self.hide_all_frames()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Clear frame first
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        # Dashboard title
        ttk.Label(
            self.dashboard_frame, text="My Medicine Dashboard", font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Today's date
        today = date.today()
        ttk.Label(
            self.dashboard_frame, 
            text=f"Today: {today.strftime('%A, %B %d, %Y')}", 
            font=("Arial", 12)
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Create two columns
        columns_frame = ttk.Frame(self.dashboard_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        left_column = ttk.Frame(columns_frame, padding=10)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_column = ttk.Frame(columns_frame, padding=10)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Today's medication section
        med_frame = ttk.LabelFrame(left_column, text="Today's Medication", padding=10)
        med_frame.pack(fill=tk.BOTH, expand=True)
        
        # Make sure logs are generated
        db.generate_medicine_logs(today, self.user_id)
        
        # Get today's medication logs
        today_logs = db.get_medicine_logs(self.user_id, today)
        
        if not today_logs:
            ttk.Label(med_frame, text="No medication scheduled for today").pack(anchor=tk.W, pady=10)
        else:
            # Create a scrollable frame for the logs
            self.create_medication_list(med_frame, today_logs)
        
        # Expiring medications section
        expire_frame = ttk.LabelFrame(right_column, text="Medications Expiring Soon", padding=10)
        expire_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get medications expiring in the next 30 days
        expiring_meds = db.get_expiring_medicines(self.user_id)
        
        if not expiring_meds:
            ttk.Label(expire_frame, text="No medications expiring soon").pack(anchor=tk.W, pady=10)
        else:
            self.create_expiring_meds_list(expire_frame, expiring_meds)
    
    def create_medication_list(self, parent, logs):
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add medication logs to scrollable frame
        self.display_medication_logs(scrollable_frame, logs)
    
    def display_medication_logs(self, parent, logs):
        now = datetime.now()
        
        for log in logs:
            log_frame = ttk.Frame(parent, padding=5)
            log_frame.pack(fill=tk.X, pady=5)
            
            scheduled_time = datetime.strptime(str(log["scheduled_time"]), "%Y-%m-%d %H:%M:%S")
            time_str = scheduled_time.strftime("%I:%M %p")
            
            # Time column
            time_frame = ttk.Frame(log_frame)
            time_frame.pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(
                time_frame, 
                text=time_str,
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W)
            
            # Medicine info column
            med_frame = ttk.Frame(log_frame)
            med_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Label(
                med_frame, 
                text=log["medicine_name"],
                font=("Arial", 11, "bold")
            ).pack(anchor=tk.W)
            
            ttk.Label(
                med_frame,
                text=f"Dosage: {log['dosage']}"
            ).pack(anchor=tk.W)
            
            # Status column
            status = log["status"]
            status_frame = ttk.Frame(log_frame)
            status_frame.pack(side=tk.RIGHT, padx=(10, 0))
            
            if status == "taken":
                taken_time = datetime.strptime(str(log["taken_time"]), "%Y-%m-%d %H:%M:%S")
                status_label = ttk.Label(
                    status_frame,
                    text="TAKEN",
                    foreground="green",
                    font=("Arial", 10, "bold")
                )
                status_label.pack(anchor=tk.E)
                
                ttk.Label(
                    status_frame,
                    text=f"at {taken_time.strftime('%I:%M %p')}",
                    foreground="green"
                ).pack(anchor=tk.E)
                
            elif status == "missed":
                status_label = ttk.Label(
                    status_frame,
                    text="MISSED",
                    foreground="red",
                    font=("Arial", 10, "bold")
                )
                status_label.pack(anchor=tk.E)
                
            elif status == "skipped":
                status_label = ttk.Label(
                    status_frame,
                    text="SKIPPED",
                    foreground="orange",
                    font=("Arial", 10, "bold")
                )
                status_label.pack(anchor=tk.E)
                
            else:  # scheduled
                if scheduled_time > now:
                    # Future dose
                    status_label = ttk.Label(
                        status_frame,
                        text="UPCOMING",
                        foreground="blue",
                        font=("Arial", 10, "bold")
                    )
                else:
                    # Due now
                    status_label = ttk.Label(
                        status_frame,
                        text="DUE NOW",
                        foreground="purple",
                        font=("Arial", 10, "bold")
                    )
                status_label.pack(anchor=tk.E)
                
                # Add action buttons
                btn_frame = ttk.Frame(status_frame)
                btn_frame.pack(pady=5)
                
                ttk.Button(
                    btn_frame,
                    text="Take",
                    command=lambda id=log["id"]: self.mark_medication(id, "taken")
                ).pack(side=tk.LEFT, padx=2)
                
                ttk.Button(
                    btn_frame,
                    text="Skip",
                    command=lambda id=log["id"]: self.mark_medication(id, "skipped")
                ).pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
    
    def create_expiring_meds_list(self, parent, medicines):
        today = date.today()
        
        for med in medicines:
            med_frame = ttk.Frame(parent, padding=5)
            med_frame.pack(fill=tk.X, pady=5)
            
            expires_on = datetime.strptime(str(med["expires_on"]), "%Y-%m-%d").date()
            days_left = (expires_on - today).days
            
            ttk.Label(
                med_frame, 
                text=med["name"], 
                font=("Arial", 11, "bold")
            ).pack(anchor=tk.W)
            
            status_color = "red" if days_left <= 7 else "orange"
            status_text = f"EXPIRES IN {days_left} DAYS!" if days_left <= 7 else f"Expires in {days_left} days"
            
            ttk.Label(
                med_frame, 
                text=status_text,
                foreground=status_color
            ).pack(anchor=tk.W)
            
            ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
    
    def mark_medication(self, log_id, status):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.update_medicine_log(log_id, status, now if status == "taken" else None)
        messagebox.showinfo("Success", f"Medication marked as {status}")
        self.show_dashboard()  # Refresh dashboard
    
    def show_schedules(self):
        self.hide_all_frames()
        self.schedules_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Clear frame first
        for widget in self.schedules_frame.winfo_children():
            widget.destroy()
        
        # Schedules title
        ttk.Label(
            self.schedules_frame, text="My Medicine Schedules", font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Add new schedule button
        ttk.Button(
            self.schedules_frame, 
            text="Add New Schedule",
            command=self.add_new_schedule
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Get all schedules
        schedules = db.get_patient_medicine_schedules(self.user_id)
        
        if not schedules:
            ttk.Label(
                self.schedules_frame, 
                text="You don't have any medicine schedules yet.",
                font=("Arial", 12)
            ).pack(anchor=tk.W, pady=20)
        else:
            self.display_schedules(schedules)
    
    def display_schedules(self, schedules):
        # Create a treeview to display schedules
        columns = ("id", "medicine", "dosage", "frequency", "time", "start_date", "end_date")
        tree = ttk.Treeview(self.schedules_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("id", text="ID")
        tree.heading("medicine", text="Medicine")
        tree.heading("dosage", text="Dosage")
        tree.heading("frequency", text="Frequency")
        tree.heading("time", text="Time Slots")
        tree.heading("start_date", text="Start Date")
        tree.heading("end_date", text="End Date")
        
        # Define column widths
        tree.column("id", width=50)
        tree.column("medicine", width=150)
        tree.column("dosage", width=100)
        tree.column("frequency", width=120)
        tree.column("time", width=150)
        tree.column("start_date", width=100)
        tree.column("end_date", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.schedules_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Add schedules to the treeview
        for schedule in schedules:
            tree.insert(
                "", 
                tk.END, 
                values=(
                    schedule["id"],
                    schedule["medicine_name"],
                    schedule["dosage"],
                    schedule["frequency"],
                    schedule["time_slots"].replace(",", ", "),
                    schedule["start_date"],
                    schedule["end_date"] if schedule["end_date"] else "Ongoing"
                )
            )
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view details
        tree.bind("<Double-1>", lambda event: self.show_schedule_details(tree))
    
    def show_schedule_details(self, tree):
        # Get selected item
        selected = tree.focus()
        if not selected:
            return
            
        # Get values
        values = tree.item(selected, "values")
        schedule_id = values[0]
        
        # Get full schedule data
        schedule = db.get_schedule_by_id(schedule_id)
        if not schedule:
            messagebox.showerror("Error", "Schedule not found")
            return
        
        # Create a popup with schedule details
        popup = tk.Toplevel(self.root)
        popup.title(f"Schedule Details: {schedule['medicine_name']}")
        popup.geometry("500x400")
        popup.transient(self.root)
        popup.grab_set()
        
        # Create a frame for the content
        content_frame = ttk.Frame(popup, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Medicine name header
        ttk.Label(
            content_frame, 
            text=schedule["medicine_name"],
            font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Schedule details
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        details = [
            ("Dosage", schedule["dosage"]),
            ("Frequency", schedule["frequency"]),
            ("Start Date", schedule["start_date"]),
            ("End Date", schedule["end_date"] if schedule["end_date"] else "Ongoing"),
            ("Time Slots", schedule["time_slots"].replace(",", ", ")),
            ("Notes", schedule["notes"] if schedule["notes"] else "None")
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(
                details_frame,
                text=f"{label}:",
                font=("Arial", 11, "bold")
            ).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            ttk.Label(
                details_frame,
                text=value
            ).grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # Medicine details if available
        if schedule["details"]:
            ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            
            ttk.Label(
                content_frame,
                text="Medicine Details:",
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W, pady=(10, 5))
            
            ttk.Label(
                content_frame,
                text=schedule["details"],
                wraplength=450
            ).pack(anchor=tk.W)
        
        # Buttons at the bottom
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Edit Schedule",
            command=lambda: self.edit_medicine_schedule(schedule, popup)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Delete Schedule",
            command=lambda: self.delete_medicine_schedule(schedule, popup)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Close",
            command=popup.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def add_new_schedule(self):
        self.show_schedule_form()
    
    def edit_medicine_schedule(self, schedule, parent_popup=None):
        if parent_popup:
            parent_popup.destroy()
        self.show_schedule_form(schedule)
    
    def show_schedule_form(self, schedule=None):
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Add Medicine Schedule" if not schedule else "Edit Medicine Schedule")
        popup.geometry("600x500")
        popup.transient(self.root)
        popup.grab_set()
        
        # Main content frame
        main_frame = ttk.Frame(popup, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form title
        title_text = "Add New Medicine Schedule" if not schedule else f"Edit Schedule: {schedule['medicine_name']}"
        ttk.Label(
            main_frame, 
            text=title_text,
            font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, expand=True)
        
        # Medicine selection
        ttk.Label(
            form_frame, 
            text="Select Medicine:",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Get all medicines
        medicines = db.get_all_medicines()
        medicine_names = [f"{m['id']} - {m['name']}" for m in medicines]
        
        medicine_var = tk.StringVar()
        if schedule:
            medicine_var.set(f"{schedule['medicine_id']} - {schedule['medicine_name']}")
        
        medicine_combo = ttk.Combobox(form_frame, textvariable=medicine_var, width=40)
        medicine_combo['values'] = medicine_names
        medicine_combo.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Dosage
        ttk.Label(
            form_frame, 
            text="Dosage:",
            font=("Arial", 11, "bold")
        ).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        dosage_var = tk.StringVar()
        if schedule:
            dosage_var.set(schedule['dosage'])
        
        ttk.Entry(form_frame, textvariable=dosage_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Frequency
        ttk.Label(
            form_frame, 
            text="Frequency:",
            font=("Arial", 11, "bold")
        ).grid(row=2, column=0, sticky=tk.W, pady=10)
        
        frequency_var = tk.StringVar()
        if schedule:
            frequency_var.set(schedule['frequency'])
        
        ttk.Entry(form_frame, textvariable=frequency_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Time slots
        ttk.Label(
            form_frame, 
            text="Time Slots (HH:MM):",
            font=("Arial", 11, "bold")
        ).grid(row=3, column=0, sticky=tk.W, pady=10)
        
        time_slots_var = tk.StringVar()
        if schedule:
            time_slots_var.set(schedule['time_slots'])
        
        ttk.Entry(form_frame, textvariable=time_slots_var, width=30).grid(row=3, column=1, sticky=tk.W, pady=10)
        ttk.Label(
            form_frame, 
            text="e.g. 08:00,12:00,18:00",
            font=("Arial", 8)
        ).grid(row=3, column=2, sticky=tk.W, pady=10)
        
        # Start Date
        ttk.Label(
            form_frame, 
            text="Start Date:",
            font=("Arial", 11, "bold")
        ).grid(row=4, column=0, sticky=tk.W, pady=10)
        
        start_date = DateEntry(
            form_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        if schedule:
            start_date_obj = datetime.strptime(str(schedule['start_date']), "%Y-%m-%d").date()
            start_date.set_date(start_date_obj)
        
        start_date.grid(row=4, column=1, sticky=tk.W, pady=10)
        
        # End Date
        ttk.Label(
            form_frame, 
            text="End Date (optional):",
            font=("Arial", 11, "bold")
        ).grid(row=5, column=0, sticky=tk.W, pady=10)
        
        end_date = DateEntry(
            form_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        if schedule and schedule['end_date']:
            end_date_obj = datetime.strptime(str(schedule['end_date']), "%Y-%m-%d").date()
            end_date.set_date(end_date_obj)
        
        end_date.grid(row=5, column=1, sticky=tk.W, pady=10)
        
        # Notes
        ttk.Label(
            form_frame, 
            text="Notes:",
            font=("Arial", 11, "bold")
        ).grid(row=6, column=0, sticky=tk.NW, pady=10)
        
        notes_text = tk.Text(form_frame, width=30, height=4)
        notes_text.grid(row=6, column=1, sticky=tk.W, pady=10)
        
        if schedule and schedule['notes']:
            notes_text.insert("1.0", schedule['notes'])
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        save_command = lambda: self.save_schedule(
            popup,
            schedule['id'] if schedule else None,
            medicine_var.get(),
            dosage_var.get(),
            frequency_var.get(),
            time_slots_var.get(),
            start_date.get_date(),
            end_date.get_date(),
            notes_text.get("1.0", tk.END).strip()
        )
        
        ttk.Button(
            button_frame,
            text="Save",
            command=save_command
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def save_schedule(self, popup, schedule_id, medicine_str, dosage, frequency, time_slots, start_date, end_date, notes):
        # Validate fields
        if not medicine_str or not dosage or not frequency or not time_slots:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Extract medicine ID from selection
        try:
            medicine_id = int(medicine_str.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Invalid medicine selection")
            return
        
        # Validate time slots format (HH:MM,HH:MM)
        time_slots_list = time_slots.split(",")
        for slot in time_slots_list:
            slot = slot.strip()
            if not slot:
                continue
                
            try:
                parts = slot.split(":")
                if len(parts) != 2:
                    raise ValueError
                    
                hour = int(parts[0])
                minute = int(parts[1])
                
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError
            except:
                messagebox.showerror("Error", f"Invalid time slot format: {slot}. Please use HH:MM format.")
                return
        
        # Format dates
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None
        
        try:
            if schedule_id:
                # Update existing schedule
                db.update_medicine_schedule(
                    schedule_id,
                    medicine_id,
                    dosage,
                    frequency,
                    start_date_str,
                    end_date_str,
                    time_slots,
                    notes
                )
                messagebox.showinfo("Success", "Medicine schedule updated successfully")
            else:
                # Add new schedule
                db.add_medicine_schedule(
                    self.user_id,
                    medicine_id,
                    None,  # No prescription ID
                    dosage,
                    frequency,
                    start_date_str,
                    end_date_str,
                    time_slots,
                    notes
                )
                messagebox.showinfo("Success", "Medicine schedule added successfully")
            
            popup.destroy()
            self.show_schedules()  # Refresh schedules view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save schedule: {str(e)}")
    
    def delete_medicine_schedule(self, schedule, parent_popup):
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the schedule for {schedule['medicine_name']}?"
        )
        
        if confirm:
            try:
                db.delete_medicine_schedule(schedule["id"])
                messagebox.showinfo(
                    "Success", 
                    f"Schedule for {schedule['medicine_name']} deleted successfully"
                )
                
                # Close the popup and refresh the schedules view
                parent_popup.destroy()
                self.show_schedules()
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Failed to delete schedule: {str(e)}"
                )
    
    def show_prescriptions(self):
        self.hide_all_frames()
        self.prescriptions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Clear frame first
        for widget in self.prescriptions_frame.winfo_children():
            widget.destroy()
        
        # Prescriptions title
        ttk.Label(
            self.prescriptions_frame, text="My Prescriptions", font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Upload prescription button
        ttk.Button(
            self.prescriptions_frame, 
            text="Upload New Prescription",
            command=self.upload_prescription
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Get all prescriptions
        prescriptions = db.get_patient_prescriptions(self.user_id)
        
        if not prescriptions:
            ttk.Label(
                self.prescriptions_frame, 
                text="You don't have any prescriptions yet.",
                font=("Arial", 12)
            ).pack(anchor=tk.W, pady=20)
        else:
            self.display_prescriptions(prescriptions)
    
    def display_prescriptions(self, prescriptions):
        prescriptions_container = ttk.Frame(self.prescriptions_frame)
        prescriptions_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for many prescriptions
        canvas = tk.Canvas(prescriptions_container)
        scrollbar = ttk.Scrollbar(prescriptions_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add prescriptions to scrollable frame
        for prescription in prescriptions:
            p_frame = ttk.Frame(scrollable_frame, padding=10)
            p_frame.pack(fill=tk.X, pady=5)
            
            # Format date
            prescription_date = prescription["prescription_date"]
            if not isinstance(prescription_date, str):
                date_str = prescription_date.strftime("%B %d, %Y") 
            else:
                date_str = prescription_date
            
            # Prescription date and doctor
            ttk.Label(
                p_frame,
                text=f"Prescription Date: {date_str}",
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W)
            
            if prescription["doctor_name"]:
                ttk.Label(p_frame, text=f"Doctor: {prescription['doctor_name']}").pack(anchor=tk.W)
            
            # Notes
            if prescription["notes"]:
                ttk.Label(
                    p_frame,
                    text=f"Notes: {prescription['notes']}",
                    wraplength=600
                ).pack(anchor=tk.W, pady=5)
            
            # Action buttons
            btn_frame = ttk.Frame(p_frame)
            btn_frame.pack(anchor=tk.W, pady=5)
            
            if prescription["file_path"]:
                ttk.Button(
                    btn_frame,
                    text="View Prescription",
                    command=lambda path=prescription["file_path"]: self.view_prescription(path)
                ).pack(side=tk.LEFT, padx=5)
            
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
    
    def upload_prescription(self):
        file_path = filedialog.askopenfilename(
            title="Select Prescription File",
            filetypes=[("PDF Files", "*.pdf"), ("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            db.add_prescription(self.user_id, file_path)
            messagebox.showinfo("Success", "Prescription uploaded successfully")
            self.show_prescriptions()  # Refresh prescriptions view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload prescription: {str(e)}")
    
    def view_prescription(self, file_path):
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open prescription: {str(e)}")
    
    def go_back_to_home(self):
        if self.parent_app:
            self.parent_app.show()
            self.root.withdraw()
        else:
            messagebox.showinfo("Information", "No parent app to return to")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()