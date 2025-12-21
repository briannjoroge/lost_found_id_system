# MUT ID Tracker

**MUT ID Tracker** is a web-based "Lost and Found" system designed specifically for managing lost Student IDs and National IDs within Murang'a University of Technology. It streamlines the process of reporting lost items, finding them, and verifying ownership before return.

## Key Features

### 👤 For Students (Public)

- **Report Lost IDs:** Submit details about a lost ID to alert the community.
- **Report Found IDs:** Upload photos and details of IDs found on campus.
- **Search & Claim:** Browse found items and submit a claim request if you spot your ID.
- **Real-time Status:** Track the status of your claim (Pending, Approved, Rejected).
- **Secure Profile:** Manage your personal details and contact information.

### For Admins (Restricted)

- **Analytics Dashboard:** View real-time statistics (Total Lost, Total Found, Pending Claims) and recent activity.
- **Claim Verification:** Review claims with a side-by-side comparison of the student's details vs. the ID card image.
- **Manage Items:** View all reports and delete spam or resolved items.
- **User Management:** View registered students and perform "Soft Deletion" (Deactivate/Restore users) to ban bad actors.
- **Secure Login:** Dedicated admin login portal with role-based access control.

---

## Techologies Used

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Authentication:** Flask-Login & Werkzeug Security

---

## Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/briannjoroge/lost_found_id_system.git](https://github.com/briannjoroge/lost_found_id_system.git)
cd lost_found_id_system
```

### 2. Set up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` in the root directory (same folder as `app.py`) to keep your configuration secure. Add the following line:

```Plaintext
FLASK_SECRET_KEY=your_very_strong_secret_key_here
```

> **How to generate a strong key:** You can run one of the following commands in your terminal:

- **Option 1 (OpenSSL - Recommended):**

```Bash
openssl rand -hex 32
```

- **Option 2 (Python):**

```Bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### 5. Initialize the Database

The application will automatically create the database file (`lostfound.db`) on the first run, but you need to verify the schema.

```bash
python
>>> from db import init_db
>>> init_db()
>>> exit()
```

### 6. Run the Application

```bash
python app.py or py app.py
```

Open your browser and navigate to: http://127.0.0.1:5000/

## Creating an Admin Account

By default, all new sign-ups are Students. To access the Admin Panel, you must elevate a user manually in the database.

1. Register a new account (e.g., `user@gmail.com`).

1. Open the database using a tool like DB Browser for SQLite.

1. Run the following SQL command:

```sql
UPDATE users SET role = 'admin' WHERE email = 'user@gmail.com';
```

4. Access the admin panel at: http://127.0.0.1:5000/admin

## 📸 Screenshots

### 📱 Student Interface

**Home Page**
The landing page where students can view lost or found items.
<img src="screenshots/home_page.png" alt="Home Page" width="800">

**2. Claiming an Item**
Students can view details of a found ID and submit a claim request if it belongs to them.
<img src="screenshots/claim_id.png" alt="Claim Process" width="800">

**3. Student Dashboard (Status Tracking)**
A personal dashboard where students can track the status of their lost reports and see if their claims are **Pending**, **Approved**, or **Rejected**.
<img src="screenshots/student_dashboard.png" alt="Student Dashboard" width="800">

---

### 🛡️ Admin Panel

**1. Restricted Admin Login**
A secure, separate login portal with password visibility toggle.
<img src="screenshots/admin_login.png" alt="Admin Login" width="800">

**2. Analytics Dashboard**
Real-time overview of lost/found statistics and quick access to recent claims.
<img src="screenshots/admin_dashboard.png" alt="Admin Dashboard" width="800">

**3. Claim Verification**
Side-by-side comparison of the claimant's details vs. the found ID card for easy verification.
<img src="screenshots/manage_claims.png" alt="Manage Claims" width="800">

## 🤝 Contributing

1. Fork the repository.

1. Create a new branch (git checkout -b feature-branch).

1. Commit your changes.

1. Push to the branch and open a Pull Request.

### Developed by Brian Njoroge
