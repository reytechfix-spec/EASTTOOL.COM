from flask import Flask, render_template, request, jsonify, session
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Data files
USERS_FILE = 'users.json'
PENDING_FILE = 'pending_users.json'
DEVICES_FILE = 'devices.json'
LICENSES_FILE = 'licenses.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            if "REYTECHFX" not in users:
                users["REYTECHFX"] = {
                    "password": hash_password("valentina241"),
                    "email": "reytechfix@gmail.com",
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.now().isoformat(),
                    "license_expiry": (datetime.now() + timedelta(days=3650)).isoformat()
                }
                save_users(users)
            return users
    return {
        "REYTECHFX": {
            "password": hash_password("valentina241"),
            "email": "reytechfix@gmail.com",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "license_expiry": (datetime.now() + timedelta(days=3650)).isoformat()
        }
    }

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_pending(pending):
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=4)

def load_devices():
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=4)

def load_licenses():
    if os.path.exists(LICENSES_FILE):
        with open(LICENSES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_licenses(licenses):
    with open(LICENSES_FILE, 'w') as f:
        json.dump(licenses, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        if not username or len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'})
        if not password or len(password) < 4:
            return jsonify({'success': False, 'error': 'Password must be at least 4 characters'})
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email is required'})
        
        users = load_users()
        pending = load_pending()
        
        if username in users:
            return jsonify({'success': False, 'error': 'Username already exists'})
        if username in pending:
            return jsonify({'success': False, 'error': 'Username already pending approval'})
        
        pending[username] = {
            'password': hash_password(password),
            'email': email,
            'registered_at': datetime.now().isoformat()
        }
        save_pending(pending)
        
        return jsonify({'success': True, 'message': 'Registration successful! Awaiting admin approval.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        users = load_users()
        pending = load_pending()
        
        if username in pending:
            return jsonify({'success': False, 'error': 'Account pending admin approval'})
        if username not in users:
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        
        user = users[username]
        if user['password'] != hash_password(password):
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        if not user.get('is_active', True):
            return jsonify({'success': False, 'error': 'Account deactivated. Contact admin.'})
        
        session['username'] = username
        session['role'] = user.get('role', 'user')
        
        return jsonify({'success': True, 'username': username, 'role': session['role']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username'], 'role': session.get('role', 'user')})
    return jsonify({'logged_in': False})

@app.route('/api/user/devices', methods=['GET'])
def get_user_devices():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    devices = load_devices()
    user_devices = devices.get(session['username'], [])
    
    # Add time remaining for each device
    users = load_users()
    user = users.get(session['username'], {})
    license_expiry = user.get('license_expiry')
    
    time_remaining = "Unlimited"
    if license_expiry:
        expiry_date = datetime.fromisoformat(license_expiry)
        if datetime.now() > expiry_date:
            time_remaining = "Expired"
        else:
            days = (expiry_date - datetime.now()).days
            time_remaining = f"{days} days"
    
    return jsonify({'success': True, 'devices': user_devices, 'time_remaining': time_remaining})

@app.route('/api/user/add_device', methods=['POST'])
def add_device():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    device_model = data.get('device_model', '')
    screenshot = data.get('screenshot', '')
    
    devices = load_devices()
    if session['username'] not in devices:
        devices[session['username']] = []
    
    devices[session['username']].append({
        'device_model': device_model,
        'screenshot': screenshot,
        'date': datetime.now().isoformat(),
        'status': 'completed'
    })
    
    save_devices(devices)
    return jsonify({'success': True, 'message': 'Device added successfully!'})

@app.route('/api/user/time_remaining', methods=['GET'])
def get_time_remaining():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    users = load_users()
    user = users.get(session['username'], {})
    license_expiry = user.get('license_expiry')
    
    if not license_expiry:
        return jsonify({'success': True, 'time_remaining': 'No license', 'days': 0})
    
    expiry_date = datetime.fromisoformat(license_expiry)
    if datetime.now() > expiry_date:
        return jsonify({'success': True, 'time_remaining': 'Expired', 'days': 0})
    
    days = (expiry_date - datetime.now()).days
    hours = (expiry_date - datetime.now()).seconds // 3600
    
    return jsonify({'success': True, 'time_remaining': f'{days} days {hours} hours', 'days': days})

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/pending_users', methods=['GET'])
def get_pending_users():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    pending = load_pending()
    pending_list = [{'username': u, 'email': d['email'], 'registered_at': d['registered_at']} for u, d in pending.items()]
    return jsonify({'success': True, 'users': pending_list})

@app.route('/api/admin/approve_user', methods=['POST'])
def approve_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    duration = data.get('duration', '30')  # days
    
    pending = load_pending()
    users = load_users()
    
    if username not in pending:
        return jsonify({'success': False, 'error': 'User not found'})
    
    user_data = pending[username]
    
    # Calculate expiry date
    expiry_date = datetime.now() + timedelta(days=int(duration))
    
    users[username] = {
        'password': user_data['password'],
        'email': user_data['email'],
        'role': 'user',
        'is_active': True,
        'created_at': user_data['registered_at'],
        'approved_by': session['username'],
        'approved_at': datetime.now().isoformat(),
        'license_expiry': expiry_date.isoformat()
    }
    
    del pending[username]
    
    save_users(users)
    save_pending(pending)
    
    return jsonify({'success': True, 'message': f'User {username} approved for {duration} days!'})

@app.route('/api/admin/reject_user', methods=['POST'])
def reject_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    
    pending = load_pending()
    if username in pending:
        del pending[username]
        save_pending(pending)
    
    return jsonify({'success': True, 'message': f'User {username} rejected!'})

@app.route('/api/admin/all_users', methods=['GET'])
def get_all_users():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    users = load_users()
    devices = load_devices()
    user_list = []
    for username, data in users.items():
        # Calculate remaining time
        time_left = "Unlimited"
        expiry = data.get('license_expiry')
        if expiry and username != 'REYTECHFX':
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                time_left = "Expired"
            else:
                days = (expiry_date - datetime.now()).days
                time_left = f"{days} days"
        
        user_list.append({
            'username': username,
            'email': data['email'],
            'role': data.get('role', 'user'),
            'is_active': data.get('is_active', True),
            'devices_count': len(devices.get(username, [])),
            'time_left': time_left,
            'created_at': data.get('created_at', ''),
            'license_expiry': expiry
        })
    
    return jsonify({'success': True, 'users': user_list})

@app.route('/api/admin/extend_license', methods=['POST'])
def extend_license():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    days = int(data.get('days', 30))
    
    if username == 'REYTECHFX':
        return jsonify({'success': False, 'error': 'Cannot modify admin'})
    
    users = load_users()
    if username not in users:
        return jsonify({'success': False, 'error': 'User not found'})
    
    current_expiry = users[username].get('license_expiry')
    if current_expiry:
        new_expiry = datetime.fromisoformat(current_expiry) + timedelta(days=days)
    else:
        new_expiry = datetime.now() + timedelta(days=days)
    
    users[username]['license_expiry'] = new_expiry.isoformat()
    save_users(users)
    
    return jsonify({'success': True, 'message': f'License extended by {days} days!'})

@app.route('/api/admin/deactivate_user', methods=['POST'])
def deactivate_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    action = data.get('action', 'deactivate')
    
    if username == 'REYTECHFX':
        return jsonify({'success': False, 'error': 'Cannot modify admin'})
    
    users = load_users()
    if username in users:
        users[username]['is_active'] = (action == 'activate')
        save_users(users)
    
    status = 'activated' if action == 'activate' else 'deactivated'
    return jsonify({'success': True, 'message': f'User {username} {status}!'})

@app.route('/api/admin/user_devices', methods=['POST'])
def admin_get_devices():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    devices = load_devices()
    user_devices = devices.get(username, [])
    
    return jsonify({'success': True, 'devices': user_devices})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
