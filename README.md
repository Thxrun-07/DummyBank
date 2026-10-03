# DummyBank - Banking & Login Portal with Excel (.xlsx) Storage

[![GitHub Repo](https://img.shields.io/badge/GitHub-thxrun--07%2FDummyBank-181717?logo=github)](https://github.com/thxrun-07/DummyBank)

A modern, responsive, and secure banking authentication web application built with **Python (Flask)**, **openpyxl**, and **Tailwind CSS**. User accounts, registrations, and login attempts are dynamically saved and synchronized into an Excel workbook (`users_data.xlsx`).

---

## 🌟 Features

- **Direct Excel Spreadsheet Storage**:
  - Automatically initializes and manages `users_data.xlsx`.
  - **Sheet 1: `Users`**: Storing User ID, Full Name, Username, Email, Role, Plain-text Password, Registration Date, Last Login Timestamp, and Login Counter.
  - **Sheet 2: `Login_History`**: Audit trail logging every login attempt (Timestamp, Success/Failed status, IP address, and User-Agent).
  - Passwords stored in plain text directly in the `.xlsx` sheet as requested.
- **Modern UI & UX**:
  - Dual-mode card: Instant switching between **Sign In** and **Sign Up**.
  - Password visibility toggle (eye icon).
  - Clean Dark/Emerald theme with glassmorphism and animated feedback.
- **Personalized User Dashboard**:
  - Displays user profile, avatar, registration time, last login time, and session statistics.
  - Live table preview of existing Excel records directly from the database.
- **Admin Only Download & Viewer (`admin@123`)**:
  - Only the authorized administrator account can access the download button and download the `.xlsx` file.
  - Regular users cannot see or access the download buttons or admin records.
  - Server-side enforcement (HTTP 403 Forbidden) prevents unauthorized direct API downloads.

---


## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```text
DummyBank/
├── app.py               # Flask web server and API routes
├── excel_manager.py     # Thread-safe Excel database manager (openpyxl)
├── users_data.xlsx      # Generated Excel spreadsheet storing all data
├── requirements.txt     # Python dependencies
├── templates/
│   ├── index.html       # Landing page (Sign In / Register / Dashboard)
│   └── admin.html       # Live Excel spreadsheet data viewer
└── static/
    ├── css/
    │   └── style.css    # Custom styles & animations
    └── js/
        ├── app.js       # Authentication & Dashboard scripts
        └── admin.js     # Excel viewer & search scripts
```

---

## 📊 Excel Spreadsheet Schema

### Sheet: `Users`
| Column | Description |
|---|---|
| **User ID** | Auto-incrementing numerical identifier |
| **Full Name** | User's full name |
| **Username** | Unique account username |
| **Email** | Unique contact email |
| **Role** | Account role (`Admin` or `User`) |
| **Password** | Account password stored in plain text |
| **Registration Date** | Timestamp when account was created |
| **Last Login Date** | Timestamp of most recent successful login |
| **Login Count** | Number of successful logins |

### Sheet: `Login_History`
| Column | Description |
|---|---|
| **Log ID** | Auto-incrementing log entry ID |
| **Username / Email** | Attempted credential identifier |
| **Attempt Time** | Timestamp of the login event |
| **Status** | `SUCCESS` (green) or `FAILED` (red) |
| **IP Address** | Client IP address |
| **User Agent** | Client browser / device information |
