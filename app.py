import os
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from excel_manager import (
    init_excel_file,
    register_user,
    authenticate_user,
    get_all_records,
    EXCEL_FILE,
    ADMIN_USERNAME
)

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Ensure Excel file and admin account are initialized on startup
init_excel_file()

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or "127.0.0.1"

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/admin')
def admin_view():
    user = session.get('user')
    # Strictly restrict admin page to admin@123
    if not user or not user.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('admin.html', user=user)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not full_name:
        return jsonify({"success": False, "message": "Full name is required."}), 400
    if not username or len(username) < 3:
        return jsonify({"success": False, "message": "Username must be at least 3 characters."}), 400
    if not email or "@" not in email:
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400
    if not password or len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    success, message, user_data = register_user(full_name, username, email, password)
    if success:
        session['user'] = user_data
        return jsonify({
            "success": True, 
            "message": "Account created and saved to Excel sheet successfully!",
            "user": user_data
        })
    else:
        return jsonify({"success": False, "message": message}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')
    ip_addr = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')

    if not identifier or not password:
        return jsonify({"success": False, "message": "Please enter both username/email and password."}), 400

    success, message, user_data = authenticate_user(identifier, password, ip_addr, user_agent)
    if success:
        session['user'] = user_data
        return jsonify({
            "success": True, 
            "message": "Welcome back! Login verified.",
            "user": user_data
        })
    else:
        return jsonify({"success": False, "message": message}), 401

@app.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/session', methods=['GET'])
def api_session():
    user = session.get('user')
    if user:
        return jsonify({"authenticated": True, "user": user})
    return jsonify({"authenticated": False, "user": None})

@app.route('/api/excel-data', methods=['GET'])
def api_excel_data():
    user = session.get('user')
    # Strictly restrict Excel database reading to admin@123
    if not user or not user.get('is_admin'):
        return jsonify({"success": False, "message": "Access Denied: Only admin@123 can view Excel records."}), 403

    records = get_all_records()
    return jsonify({
        "success": True,
        "users": records["users"],
        "logs": records["logs"],
        "file_name": os.path.basename(EXCEL_FILE),
        "total_users": len(records["users"]),
        "total_logs": len(records["logs"])
    })

@app.route('/download-excel')
def download_excel():
    user = session.get('user')
    # Strictly restrict download privileges to admin@123
    if not user or not user.get('is_admin'):
        return jsonify({
            "success": False,
            "error": "Forbidden", 
            "message": "Access Denied: Only administrator (admin@123) has permission to download the Excel sheet."
        }), 403

    if not os.path.exists(EXCEL_FILE):
        init_excel_file()
    return send_file(
        EXCEL_FILE,
        as_attachment=True,
        download_name="users_data.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    print("Starting Login Website on http://127.0.0.1:5000")
    print(f"Data will be stored in: {EXCEL_FILE}")
    print(f"Admin Username: {ADMIN_USERNAME}")
    app.run(host='127.0.0.1', port=5000, debug=True)
