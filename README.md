# Medical Management App

A comprehensive medical management system built with Python and Tkinter that helps patients and medical staff manage medications, prescriptions, and medicine schedules.

## Features

- 🏥 **Multi-user System**
  - Patient Interface
  - Admin Interface
  - Doctor Interface (coming soon)

- 💊 **Medicine Management**
  - Complete inventory management
  - Track medicine quantities
  - Monitor expiry dates
  - Prescription requirements tracking

- 📅 **Medicine Schedules**
  - Create and manage medicine schedules
  - Track medication times
  - Mark medicines as taken/skipped
  - Get notifications for upcoming doses

- 📋 **Prescription Management**
  - Upload and store prescriptions
  - View prescription history
  - Track prescription-based schedules
  - Doctor assignment

## Installation

1. Ensure you have Python 3.11 or later installed

2. Clone the repository:
   ```bash
   git clone https://github.com/Puneetprajapat/Medical-Management-App.git
   cd Medical-Management-App
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up MySQL database:
   - Install MySQL Server
   - Create a user with username "root" and password "1234"
   - The application will automatically create the database and required tables

## Dependencies

- Python 3.11+
- mysql-connector-python
- tkcalendar
- Pillow
- tkinter (comes with Python)

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Login using demo credentials:
   - Admin: username: "admin", password: "admin123"
   - Patient: username: "patient1", password: "password123"
   - Doctor: username: "doctor1", password: "doctor123"

## Features Details

### Admin Interface

- Manage medicine inventory
- Add new medicines
- Remove medicines
- Track stock levels
- Monitor expiry dates

### Patient Interface

#### Dashboard
- View today's medication schedule
- Track medication status
- Monitor expiring medicines
- Mark medicines as taken/skipped

#### Medicine Schedules
- Create custom medicine schedules
- Set dosage and frequency
- Configure time slots
- Add notes and instructions
- Edit or delete schedules

#### Prescriptions
- Upload prescription files
- View prescription history
- Track doctor assignments
- Access prescription details

## Database Structure

The application uses MySQL with the following tables:

- `users` - User information and authentication
- `medicines` - Medicine inventory and details
- `prescriptions` - Patient prescriptions and records
- `medicine_schedules` - Medication schedules
- `medicine_logs` - Medication tracking logs

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
