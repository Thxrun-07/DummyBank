import os
import io
from datetime import datetime
from threading import Lock
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users_data.xlsx")
excel_lock = Lock()

ADMIN_USERNAME = "admin@123"
ADMIN_PASSWORD = "Admin@123"

HEADER_FILL_USERS = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Deep Blue
HEADER_FILL_LOGS = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid")   # Teal
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ROW_FONT = Font(name="Calibri", size=10)
BORDER_THIN = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)

USERS_HEADERS = [
    "User ID", "Full Name", "Username", "Email", "Role",
    "Password", "Registration Date", "Last Login Date", "Login Count"
]

LOGS_HEADERS = [
    "Log ID", "Username / Email", "Attempt Time", 
    "Status", "IP Address", "User Agent"
]

def _load_workbook():
    """Safely loads workbook from bytes in memory so it can be read even when open in Microsoft Excel."""
    with open(EXCEL_FILE, "rb") as f:
        return openpyxl.load_workbook(io.BytesIO(f.read()))

def init_excel_file():
    """Initializes the Excel workbook if not present, and ensures admin credentials exist without crashing on startup."""
    with excel_lock:
        if not os.path.exists(EXCEL_FILE):
            wb = openpyxl.Workbook()
            
            # 1. Sheet: Users
            ws_users = wb.active
            ws_users.title = "Users"
            ws_users.append(USERS_HEADERS)
            
            for col_idx in range(1, len(USERS_HEADERS) + 1):
                cell = ws_users.cell(row=1, column=col_idx)
                cell.fill = HEADER_FILL_USERS
                cell.font = HEADER_FONT
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = BORDER_THIN
            ws_users.row_dimensions[1].height = 26

            # 2. Sheet: Login Logs
            ws_logs = wb.create_sheet(title="Login_History")
            ws_logs.append(LOGS_HEADERS)
            for col_idx in range(1, len(LOGS_HEADERS) + 1):
                cell = ws_logs.cell(row=1, column=col_idx)
                cell.fill = HEADER_FILL_LOGS
                cell.font = HEADER_FONT
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = BORDER_THIN
            ws_logs.row_dimensions[1].height = 26

            # Seed Admin Account with plain-text password
            reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            admin_row = [
                1,
                "System Administrator",
                ADMIN_USERNAME,
                "admin@system.local",
                "Admin",
                ADMIN_PASSWORD,
                reg_time,
                "Never",
                0
            ]
            ws_users.append(admin_row)
            _style_row(ws_users, ws_users.max_row, len(admin_row))

            _autofit_columns(ws_users)
            _autofit_columns(ws_logs)

            try:
                wb.save(EXCEL_FILE)
            except PermissionError:
                print(f"[WARNING] Cannot create {EXCEL_FILE}: file is locked. Close it in Excel.")
            except Exception as e:
                print(f"[WARNING] Error saving initial Excel workbook: {e}")
        else:
            # File exists - verify admin account exists without rewriting unless needed
            try:
                wb = _load_workbook()
                if "Users" in wb.sheetnames:
                    ws_users = wb["Users"]
                    admin_found = False
                    needs_save = False

                    for row in range(2, ws_users.max_row + 1):
                        u_val = ws_users.cell(row=row, column=3).value
                        if u_val and str(u_val).strip().lower() == ADMIN_USERNAME.lower():
                            admin_found = True
                            if str(ws_users.cell(row=row, column=6).value) != ADMIN_PASSWORD:
                                ws_users.cell(row=row, column=6).value = ADMIN_PASSWORD
                                needs_save = True
                            break
                    
                    if not admin_found:
                        reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_id = ws_users.max_row
                        admin_row = [
                            new_id,
                            "System Administrator",
                            ADMIN_USERNAME,
                            "admin@system.local",
                            "Admin",
                            ADMIN_PASSWORD,
                            reg_time,
                            "Never",
                            0
                        ]
                        ws_users.append(admin_row)
                        _style_row(ws_users, ws_users.max_row, len(admin_row))
                        needs_save = True

                    if needs_save:
                        _autofit_columns(ws_users)
                        try:
                            wb.save(EXCEL_FILE)
                        except PermissionError:
                            print(f"[NOTICE] {EXCEL_FILE} is open in Excel. Will use in-memory state until file is closed.")
            except Exception as e:
                print(f"[NOTICE] Existing Excel workbook inspected: {e}")

def _style_row(ws, row_idx, col_count):
    ws.row_dimensions[row_idx].height = 22
    for col_idx in range(1, col_count + 1):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.font = ROW_FONT
        cell.border = BORDER_THIN
        if col_idx in (1, 5, 7, 8, 9):
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

def _autofit_columns(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

def register_user(full_name: str, username: str, email: str, password: str):
    """
    Registers a new regular user into the Excel sheet with plain-text password.
    """
    init_excel_file()
    username_clean = username.strip().lower()
    email_clean = email.strip().lower()

    if username_clean == ADMIN_USERNAME.lower():
        return False, "This username is reserved for administration.", None

    with excel_lock:
        try:
            wb = _load_workbook()
        except PermissionError:
            return False, "Cannot register: 'users_data.xlsx' is currently open in Microsoft Excel. Please close it in Excel and try again.", None
        except Exception as e:
            return False, f"Error reading Excel sheet: {e}", None

        ws_users = wb["Users"]

        # Check for duplicates
        existing_id = 0
        for row in range(2, ws_users.max_row + 1):
            u_val = ws_users.cell(row=row, column=3).value
            e_val = ws_users.cell(row=row, column=4).value
            curr_id = ws_users.cell(row=row, column=1).value
            if curr_id and isinstance(curr_id, int) and curr_id > existing_id:
                existing_id = curr_id

            if u_val and str(u_val).strip().lower() == username_clean:
                return False, "Username is already registered.", None
            if e_val and str(e_val).strip().lower() == email_clean:
                return False, "Email is already registered.", None

        new_id = existing_id + 1
        reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Storing password in plain text as requested
        row_data = [
            new_id,
            full_name.strip(),
            username.strip(),
            email.strip(),
            "User",
            password,
            reg_time,
            "Never",
            0
        ]
        ws_users.append(row_data)
        _style_row(ws_users, ws_users.max_row, len(row_data))

        _autofit_columns(ws_users)
        try:
            wb.save(EXCEL_FILE)
        except PermissionError:
            return False, "Cannot save new user: 'users_data.xlsx' is currently open in Microsoft Excel. Please close the file in Excel and try again.", None

        return True, "Registration successful!", {
            "id": new_id,
            "full_name": full_name.strip(),
            "username": username.strip(),
            "email": email.strip(),
            "role": "User",
            "is_admin": False,
            "registered_at": reg_time
        }

def authenticate_user(login_identifier: str, password: str, ip_address: str = "127.0.0.1", user_agent: str = ""):
    """
    Authenticates user against Excel sheet records using plain-text comparison.
    Allows login even if the Excel spreadsheet is open in Excel desktop.
    """
    init_excel_file()
    ident_clean = login_identifier.strip().lower()
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with excel_lock:
        try:
            wb = _load_workbook()
        except Exception as e:
            return False, f"Could not access Excel database: {e}", None

        ws_users = wb["Users"]
        ws_logs = wb["Login_History"]

        user_data = None

        for row in range(2, ws_users.max_row + 1):
            curr_u = ws_users.cell(row=row, column=3).value
            curr_e = ws_users.cell(row=row, column=4).value
            
            if (curr_u and str(curr_u).strip().lower() == ident_clean) or \
               (curr_e and str(curr_e).strip().lower() == ident_clean):
                stored_password = str(ws_users.cell(row=row, column=6).value or "")
                role_val = str(ws_users.cell(row=row, column=5).value or "User")
                
                # Plain-text password check
                if stored_password == password:
                    prev_count = ws_users.cell(row=row, column=9).value or 0
                    try:
                        prev_count = int(prev_count)
                    except (ValueError, TypeError):
                        prev_count = 0
                    
                    ws_users.cell(row=row, column=8).value = log_time
                    ws_users.cell(row=row, column=9).value = prev_count + 1

                    is_admin = (str(curr_u).strip().lower() == ADMIN_USERNAME.lower()) or (role_val == "Admin")

                    user_data = {
                        "id": ws_users.cell(row=row, column=1).value,
                        "full_name": ws_users.cell(row=row, column=2).value,
                        "username": ws_users.cell(row=row, column=3).value,
                        "email": ws_users.cell(row=row, column=4).value,
                        "role": role_val,
                        "is_admin": is_admin,
                        "registered_at": ws_users.cell(row=row, column=7).value,
                        "last_login": log_time,
                        "login_count": prev_count + 1
                    }
                break

        # Record login history log
        log_id = ws_logs.max_row
        status_text = "SUCCESS" if user_data else "FAILED"
        log_row_data = [
            log_id,
            login_identifier.strip(),
            log_time,
            status_text,
            ip_address,
            user_agent[:120] if user_agent else "Unknown"
        ]
        ws_logs.append(log_row_data)

        new_log_row_idx = ws_logs.max_row
        ws_logs.row_dimensions[new_log_row_idx].height = 20
        status_color = "15803D" if status_text == "SUCCESS" else "B91C1C"
        for col_idx in range(1, len(log_row_data) + 1):
            cell = ws_logs.cell(row=new_log_row_idx, column=col_idx)
            cell.font = ROW_FONT
            cell.border = BORDER_THIN
            if col_idx == 4:
                cell.font = Font(name="Calibri", size=10, bold=True, color=status_color)
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in (1, 3, 5):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        _autofit_columns(ws_users)
        _autofit_columns(ws_logs)

        # Attempt to save back to Excel. If locked by Excel app, don't crash or prevent authentication
        try:
            wb.save(EXCEL_FILE)
        except PermissionError:
            pass

    if user_data:
        return True, "Login successful!", user_data
    else:
        return False, "Invalid username/email or password.", None

def get_all_records():
    """Retrieves all users and login history for the admin/data viewer dashboard."""
    init_excel_file()
    users = []
    logs = []

    with excel_lock:
        try:
            wb = _load_workbook()
        except Exception:
            return {"users": [], "logs": [], "file_path": EXCEL_FILE}

        if "Users" in wb.sheetnames:
            ws_users = wb["Users"]
            for r in range(2, ws_users.max_row + 1):
                uid = ws_users.cell(row=r, column=1).value
                if uid is not None:
                    users.append({
                        "id": uid,
                        "full_name": ws_users.cell(row=r, column=2).value or "",
                        "username": ws_users.cell(row=r, column=3).value or "",
                        "email": ws_users.cell(row=r, column=4).value or "",
                        "role": ws_users.cell(row=r, column=5).value or "User",
                        "password": str(ws_users.cell(row=r, column=6).value or ""),
                        "registered_at": str(ws_users.cell(row=r, column=7).value or ""),
                        "last_login": str(ws_users.cell(row=r, column=8).value or ""),
                        "login_count": ws_users.cell(row=r, column=9).value or 0
                    })

        if "Login_History" in wb.sheetnames:
            ws_logs = wb["Login_History"]
            for r in range(2, ws_logs.max_row + 1):
                lid = ws_logs.cell(row=r, column=1).value
                if lid is not None:
                    logs.append({
                        "log_id": lid,
                        "identifier": ws_logs.cell(row=r, column=2).value or "",
                        "timestamp": str(ws_logs.cell(row=r, column=3).value or ""),
                        "status": ws_logs.cell(row=r, column=4).value or "",
                        "ip": ws_logs.cell(row=r, column=5).value or "",
                        "user_agent": ws_logs.cell(row=r, column=6).value or ""
                    })

    return {"users": users, "logs": logs, "file_path": EXCEL_FILE}
