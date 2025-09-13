import mysql.connector as mysql
from datetime import date, timedelta, datetime
import os
import shutil


class Database:
    connection: mysql.MySQLConnection

    def __init__(self):
        self.connection = mysql.connect(
            host="localhost", user="root", password="1234"
        )
        self.create_database()
        self.create_tables()
        self.add_sample_medicines()
        self.add_sample_users()

    def get_user_by_id(self, user_id):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def create_database(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS medical_management")
        cursor.execute("USE medical_management")
        cursor.close()

    def create_tables(self):
        cursor = self.connection.cursor()

        # Users table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            user_type ENUM('patient', 'doctor', 'admin') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Medicines table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS medicines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            details TEXT,
            quantity INT NOT NULL,
            stocked_on DATE NOT NULL,
            expires_on DATE,
            manufacturer VARCHAR(255),
            batch_no VARCHAR(100),
            storage VARCHAR(100),
            prescription BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        )

        # Prescriptions table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            doctor_id INT,
            prescription_date DATE NOT NULL,
            notes TEXT,
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
        )

        # Medicine schedules table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS medicine_schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            medicine_id INT NOT NULL,
            prescription_id INT,
            dosage VARCHAR(100) NOT NULL,
            frequency VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            time_slots TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE SET NULL
        )
        """
        )

        # Medicine logs table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS medicine_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            schedule_id INT NOT NULL,
            scheduled_time DATETIME NOT NULL,
            taken_time DATETIME,
            status ENUM('scheduled', 'taken', 'missed', 'skipped') DEFAULT 'scheduled',
            notes TEXT,
            FOREIGN KEY (schedule_id) REFERENCES medicine_schedules(id) ON DELETE CASCADE
        )
        """
        )

        self.connection.commit()
        cursor.close()

    def add_sample_users(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        count = result["count"]
        cursor.close()

        if count == 0:
            sample_users = [
                {
                    "username": "patient1",
                    "password": "password123",
                    "email": "patient1@example.com",
                    "full_name": "John Smith",
                    "user_type": "patient",
                },
                {
                    "username": "patient2",
                    "password": "password123",
                    "email": "patient2@example.com",
                    "full_name": "Jane Doe",
                    "user_type": "patient",
                },
                {
                    "username": "doctor1",
                    "password": "doctor123",
                    "email": "doctor1@example.com",
                    "full_name": "Dr. Robert Johnson",
                    "user_type": "doctor",
                },
                {
                    "username": "admin",
                    "password": "admin123",
                    "email": "admin@example.com",
                    "full_name": "Admin User",
                    "user_type": "admin",
                },
            ]

            for user in sample_users:
                self.add_user(
                    username=user["username"],
                    password=user["password"],
                    email=user["email"],
                    full_name=user["full_name"],
                    user_type=user["user_type"],
                )

            # Add sample prescriptions and schedules
            self.add_sample_patient_data()

    def add_sample_patient_data(self):
        # Add sample prescription for patient1
        patient1_id = self.get_user_id_by_username("patient1")
        doctor1_id = self.get_user_id_by_username("doctor1")

        if patient1_id and doctor1_id:
            # Create prescriptions directory if it doesn't exist
            os.makedirs("prescriptions", exist_ok=True)

            # Create a sample prescription file
            sample_prescription_path = "prescriptions/patient1_prescription.txt"
            with open(sample_prescription_path, "w") as f:
                f.write("Sample prescription for patient John Smith\n")
                f.write("Prescribed by Dr. Robert Johnson\n")
                f.write("Date: " + date.today().strftime("%Y-%m-%d") + "\n\n")
                f.write(
                    "1. Paracetamol 500mg - 1 tablet three times daily after meals for 7 days\n"
                )
                f.write(
                    "2. Ibuprofen 400mg - 1 tablet twice daily with food for 5 days\n\n"
                )
                f.write("Follow up in 2 weeks.")

            prescription_id = self.add_prescription(
                patient_id=patient1_id,
                doctor_id=doctor1_id,
                prescription_date=date.today().strftime("%Y-%m-%d"),
                notes="Take medicines as prescribed. Follow up in 2 weeks.",
                file_path=sample_prescription_path,
            )

            # Add medicine schedules for patient1
            medicines = self.get_all_medicines()
            if medicines and len(medicines) >= 2:
                # Schedule for Paracetamol
                self.add_medicine_schedule(
                    patient_id=patient1_id,
                    medicine_id=medicines[0]["id"],
                    prescription_id=prescription_id,
                    dosage="1 tablet",
                    frequency="3 times daily",
                    start_date=date.today().strftime("%Y-%m-%d"),
                    end_date=(date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    time_slots="08:00,14:00,20:00",
                    notes="Take after meals",
                )

                # Schedule for Ibuprofen
                self.add_medicine_schedule(
                    patient_id=patient1_id,
                    medicine_id=medicines[1]["id"],
                    prescription_id=prescription_id,
                    dosage="1 tablet",
                    frequency="twice daily",
                    start_date=date.today().strftime("%Y-%m-%d"),
                    end_date=(date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
                    time_slots="09:00,21:00",
                    notes="Take with food to avoid stomach upset",
                )

    def add_sample_medicines(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM medicines")
        result = cursor.fetchone()
        count = result["count"]
        cursor.close()

        if count == 0:
            today = date.today()
            sample_medicines = [
                {
                    "name": "Paracetamol 500mg",
                    "details": "Pain reliever and fever reducer",
                    "quantity": 100,
                    "stocked_on": today.strftime("%Y-%m-%d"),
                    "expires_on": (today + timedelta(days=730)).strftime("%Y-%m-%d"),
                    "manufacturer": "GlaxoSmithKline",
                    "batch_no": "PCM202401",
                    "storage": "Store below 30°C in a dry place",
                    "prescription": False,
                },
                {
                    "name": "Ibuprofen 400mg",
                    "details": "Non-steroidal anti-inflammatory drug (NSAID)",
                    "quantity": 60,
                    "stocked_on": today.strftime("%Y-%m-%d"),
                    "expires_on": (today + timedelta(days=730)).strftime("%Y-%m-%d"),
                    "manufacturer": "Pfizer",
                    "batch_no": "IBU202401",
                    "storage": "Store at room temperature",
                    "prescription": False,
                },
                {
                    "name": "Amoxicillin 250mg",
                    "details": "Antibiotic used to treat bacterial infections",
                    "quantity": 30,
                    "stocked_on": today.strftime("%Y-%m-%d"),
                    "expires_on": (today + timedelta(days=365)).strftime("%Y-%m-%d"),
                    "manufacturer": "Novartis",
                    "batch_no": "AMX202401",
                    "storage": "Store below 25°C in a dry place",
                    "prescription": True,
                },
                {
                    "name": "Cetirizine 10mg",
                    "details": "Antihistamine for allergy relief",
                    "quantity": 40,
                    "stocked_on": today.strftime("%Y-%m-%d"),
                    "expires_on": (today + timedelta(days=730)).strftime("%Y-%m-%d"),
                    "manufacturer": "Sun Pharma",
                    "batch_no": "CTZ202401",
                    "storage": "Store at room temperature, away from light",
                    "prescription": False,
                },
                {
                    "name": "Omeprazole 20mg",
                    "details": "Proton pump inhibitor for acid reflux and heartburn",
                    "quantity": 28,
                    "stocked_on": today.strftime("%Y-%m-%d"),
                    "expires_on": (today + timedelta(days=730)).strftime("%Y-%m-%d"),
                    "manufacturer": "AstraZeneca",
                    "batch_no": "OMP202401",
                    "storage": "Store at room temperature, away from moisture",
                    "prescription": False,
                },
            ]

            for medicine in sample_medicines:
                self.add_medicine(
                    name=medicine["name"],
                    details=medicine["details"],
                    quantity=int(medicine["quantity"]),
                    stocked_on=medicine["stocked_on"],
                    expires_on=medicine["expires_on"],
                    manufacturer=medicine["manufacturer"],
                    batch_no=medicine["batch_no"],
                    storage=medicine["storage"],
                    prescription=medicine["prescription"],
                )

    # User management methods
    def add_user(self, username, password, email, full_name, user_type):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO users (username, password, email, full_name, user_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (username, password, email, full_name, user_type)

        cursor.execute(query, values)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def get_user_id_by_username(self, username):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        return result["id"] if result else None

    def get_user(self, username):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    # Prescription management methods
    def add_prescription(self, patient_id, file_path=None, doctor_id=None, prescription_date=None, notes=None):
        if prescription_date is None:
            prescription_date = date.today().strftime("%Y-%m-%d")

        # Create prescriptions directory if it doesn't exist
        if file_path:
            prescriptions_dir = os.path.join("prescriptions", f"user_{patient_id}")
            os.makedirs(prescriptions_dir, exist_ok=True)

            # Copy file to prescriptions directory
            file_name = os.path.basename(file_path)
            new_path = os.path.join(prescriptions_dir, file_name)

            # Copy the file
            shutil.copy2(file_path, new_path)
            file_path = new_path

        cursor = self.connection.cursor()
        query = """
        INSERT INTO prescriptions (patient_id, doctor_id, prescription_date, notes, file_path)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (patient_id, doctor_id, prescription_date, notes, file_path)

        cursor.execute(query, values)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def get_patient_prescriptions(self, patient_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT p.*, u.full_name as doctor_name 
        FROM prescriptions p 
        LEFT JOIN users u ON p.doctor_id = u.id 
        WHERE p.patient_id = %s
        ORDER BY p.prescription_date DESC
        """
        cursor.execute(query, (patient_id,))
        prescriptions = cursor.fetchall()
        cursor.close()
        return prescriptions

    def delete_prescription(self, prescription_id):
        cursor = self.connection.cursor(dictionary=True)

        # Get the file path before deleting
        query = "SELECT file_path FROM prescriptions WHERE id = %s"
        cursor.execute(query, (prescription_id,))
        result = cursor.fetchone()

        if result and result["file_path"] and os.path.exists(result["file_path"]):
            try:
                os.remove(result["file_path"])
            except:
                pass  # Continue even if file removal fails

        # Delete prescription
        query = "DELETE FROM prescriptions WHERE id = %s"
        cursor.execute(query, (prescription_id,))
        self.connection.commit()
        cursor.close()

    # Medicine methods
    def add_medicine(
        self,
        name,
        details,
        quantity,
        stocked_on,
        expires_on,
        manufacturer,
        batch_no,
        storage,
        prescription,
    ):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO medicines 
        (name, details, quantity, stocked_on, expires_on, manufacturer, batch_no, storage, prescription)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            name,
            details,
            quantity,
            stocked_on,
            expires_on,
            manufacturer,
            batch_no,
            storage,
            prescription,
        )

        cursor.execute(query, values)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def get_all_medicines(self):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM medicines ORDER BY name"
        cursor.execute(query)
        medicines = cursor.fetchall()
        cursor.close()
        return medicines

    def get_medicine_by_id(self, medicine_id):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM medicines WHERE id = %s"
        cursor.execute(query, (medicine_id,))
        medicine = cursor.fetchone()
        cursor.close()
        return medicine

    def update_medicine_quantity(self, medicine_id, new_quantity):
        cursor = self.connection.cursor()
        query = "UPDATE medicines SET quantity = %s WHERE id = %s"
        cursor.execute(query, (new_quantity, medicine_id))
        self.connection.commit()
        cursor.close()

    def remove_medicine(self, medicine_id):
        cursor = self.connection.cursor()

        # First check if this medicine is used in any schedules
        check_query = "SELECT COUNT(*) as count FROM medicine_schedules WHERE medicine_id = %s"
        cursor.execute(check_query, (medicine_id,))
        result = cursor.fetchone()

        if result[0] > 0:
            cursor.close()
            raise Exception("Cannot remove medicine that is used in patient schedules")

        # Delete the medicine
        delete_query = "DELETE FROM medicines WHERE id = %s"
        cursor.execute(delete_query, (medicine_id,))

        self.connection.commit()
        cursor.close()

    # Medicine schedule methods
    def add_medicine_schedule(
        self,
        patient_id,
        medicine_id,
        prescription_id,
        dosage,
        frequency,
        start_date,
        end_date,
        time_slots,
        notes=None,
    ):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO medicine_schedules 
        (patient_id, medicine_id, prescription_id, dosage, frequency, start_date, end_date, time_slots, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            patient_id,
            medicine_id,
            prescription_id,
            dosage,
            frequency,
            start_date,
            end_date,
            time_slots,
            notes,
        )

        cursor.execute(query, values)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()

        # Generate medicine logs for the schedule
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Generate logs for next 7 days or until end date, whichever comes first
        current_date = start_date_obj
        end_generate = date.today() + timedelta(days=7)

        while current_date <= end_generate:
            if end_date_obj and current_date > end_date_obj:
                break
            self.generate_medicine_logs_for_schedule(last_id, current_date)
            current_date += timedelta(days=1)

        return last_id

    def get_patient_medicine_schedules(self, patient_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT ms.*, m.name as medicine_name, m.details, m.expires_on
        FROM medicine_schedules ms
        JOIN medicines m ON ms.medicine_id = m.id
        WHERE ms.patient_id = %s
        ORDER BY ms.start_date DESC
        """
        cursor.execute(query, (patient_id,))
        schedules = cursor.fetchall()
        cursor.close()
        return schedules

    def get_schedule_by_id(self, schedule_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT ms.*, m.name as medicine_name, m.details 
        FROM medicine_schedules ms
        JOIN medicines m ON ms.medicine_id = m.id
        WHERE ms.id = %s
        """
        cursor.execute(query, (schedule_id,))
        schedule = cursor.fetchone()
        cursor.close()
        return schedule

    def update_medicine_schedule(
        self,
        schedule_id,
        medicine_id,
        dosage,
        frequency,
        start_date,
        end_date,
        time_slots,
        notes=None,
    ):
        cursor = self.connection.cursor()
        query = """
        UPDATE medicine_schedules
        SET medicine_id = %s, dosage = %s, frequency = %s, start_date = %s,
            end_date = %s, time_slots = %s, notes = %s
        WHERE id = %s
        """
        values = (medicine_id, dosage, frequency, start_date, end_date, time_slots, notes, schedule_id)

        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()

        # Regenerate medicine logs for updated schedule
        schedule_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        schedule_end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Delete future logs for this schedule
        self.delete_future_medicine_logs(schedule_id, schedule_start)

        # Generate new logs
        current_date = schedule_start
        while (schedule_end is None or current_date <= schedule_end) and current_date <= date.today() + timedelta(days=7):
            self.generate_medicine_logs_for_schedule(schedule_id, current_date)
            current_date += timedelta(days=1)

    def delete_medicine_schedule(self, schedule_id):
        cursor = self.connection.cursor()
        # First delete related medicine logs
        delete_logs_query = "DELETE FROM medicine_logs WHERE schedule_id = %s"
        cursor.execute(delete_logs_query, (schedule_id,))

        # Then delete the schedule
        delete_schedule_query = "DELETE FROM medicine_schedules WHERE id = %s"
        cursor.execute(delete_schedule_query, (schedule_id,))

        self.connection.commit()
        cursor.close()

    def delete_future_medicine_logs(self, schedule_id, from_date):
        cursor = self.connection.cursor()
        query = """
        DELETE FROM medicine_logs
        WHERE schedule_id = %s 
        AND DATE(scheduled_time) >= %s
        """
        cursor.execute(query, (schedule_id, from_date))
        self.connection.commit()
        cursor.close()

    def delete_future_logs(self, schedule_id):
        cursor = self.connection.cursor()
        today = date.today().strftime("%Y-%m-%d")
        query = "DELETE FROM medicine_logs WHERE schedule_id = %s AND DATE(scheduled_time) >= %s"
        cursor.execute(query, (schedule_id, today))
        self.connection.commit()
        cursor.close()

    def generate_medicine_logs_for_schedule(self, schedule_id, for_date):
        cursor = self.connection.cursor(dictionary=True)

        # Get schedule details
        query = "SELECT * FROM medicine_schedules WHERE id = %s"
        cursor.execute(query, (schedule_id,))
        schedule = cursor.fetchone()

        if not schedule:
            cursor.close()
            return

        # Check if logs already exist for this date
        query = """
        SELECT COUNT(*) as count FROM medicine_logs 
        WHERE schedule_id = %s 
        AND DATE(scheduled_time) = %s
        """
        cursor.execute(query, (schedule_id, for_date))
        result = cursor.fetchone()

        if result["count"] > 0:
            cursor.close()
            return  # Logs already exist

        # Generate logs based on time slots
        time_slots = schedule["time_slots"].split(",")

        for time_slot in time_slots:
            time_parts = time_slot.strip().split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0

            scheduled_time = datetime.combine(
                for_date, datetime.min.time().replace(hour=hour, minute=minute)
            )

            insert_query = """
            INSERT INTO medicine_logs (schedule_id, scheduled_time, status)
            VALUES (%s, %s, %s)
            """

            # Set status based on current time
            current_time = datetime.now()
            status = "scheduled"
            if scheduled_time < current_time:
                # If it's in the past, mark as missed
                time_diff = current_time - scheduled_time
                if time_diff.total_seconds() > 3600:  # More than 1 hour in the past
                    status = "missed"

            cursor.execute(insert_query, (schedule_id, scheduled_time, status))

        self.connection.commit()
        cursor.close()

    def generate_medicine_logs(self, for_date, patient_id=None):
        cursor = self.connection.cursor(dictionary=True)

        if patient_id:
            query = """
            SELECT * FROM medicine_schedules 
            WHERE patient_id = %s 
            AND start_date <= %s 
            AND (end_date IS NULL OR end_date >= %s)
            """
            cursor.execute(query, (patient_id, for_date, for_date))
        else:
            query = """
            SELECT * FROM medicine_schedules 
            WHERE start_date <= %s 
            AND (end_date IS NULL OR end_date >= %s)
            """
            cursor.execute(query, (for_date, for_date))

        schedules = cursor.fetchall()
        cursor.close()

        for schedule in schedules:
            self.generate_medicine_logs_for_schedule(schedule["id"], for_date)

    def get_medicine_logs(self, patient_id, for_date=None):
        cursor = self.connection.cursor(dictionary=True)

        if for_date:
            query = """
            SELECT ml.*, ms.dosage, m.name as medicine_name 
            FROM medicine_logs ml
            JOIN medicine_schedules ms ON ml.schedule_id = ms.id
            JOIN medicines m ON ms.medicine_id = m.id
            WHERE ms.patient_id = %s
            AND DATE(ml.scheduled_time) = %s
            ORDER BY ml.scheduled_time
            """
            cursor.execute(query, (patient_id, for_date))
        else:
            # Get logs for the next 7 days by default
            today = date.today().strftime("%Y-%m-%d")
            future_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

            query = """
            SELECT ml.*, ms.dosage, m.name as medicine_name 
            FROM medicine_logs ml
            JOIN medicine_schedules ms ON ml.schedule_id = ms.id
            JOIN medicines m ON ms.medicine_id = m.id
            WHERE ms.patient_id = %s
            AND DATE(ml.scheduled_time) BETWEEN %s AND %s
            ORDER BY ml.scheduled_time
            """
            cursor.execute(query, (patient_id, today, future_date))

        logs = cursor.fetchall()
        cursor.close()
        return logs

    def update_medicine_log(self, log_id, status, taken_time=None, notes=None):
        cursor = self.connection.cursor()

        if taken_time:
            query = """
            UPDATE medicine_logs
            SET status = %s, taken_time = %s, notes = %s
            WHERE id = %s
            """
            values = (status, taken_time, notes, log_id)
        else:
            query = """
            UPDATE medicine_logs
            SET status = %s, notes = %s
            WHERE id = %s
            """
            values = (status, notes, log_id)

        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()

    def get_expiring_medicines(self, patient_id, days=30):
        cursor = self.connection.cursor(dictionary=True)
        future_date = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")

        query = """
        SELECT DISTINCT m.* 
        FROM medicines m
        JOIN medicine_schedules ms ON m.id = ms.medicine_id
        WHERE ms.patient_id = %s
        AND m.expires_on <= %s
        AND m.expires_on >= CURDATE()
        ORDER BY m.expires_on
        """

        cursor.execute(query, (patient_id, future_date))
        medicines = cursor.fetchall()
        cursor.close()
        return medicines

    def get_all_doctors(self):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT id, full_name, email 
        FROM users 
        WHERE user_type = 'doctor'
        ORDER BY full_name
        """
        cursor.execute(query)
        doctors = cursor.fetchall()
        cursor.close()
        return doctors