from flask import Flask, render_template, request, jsonify, session
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ==================== DATA FILES ====================
USERS_FILE = 'users.json'
PENDING_FILE = 'pending_users.json'
DEVICES_FILE = 'devices.json'
REVIEWS_FILE = 'reviews.json'
STATS_FILE = 'stats.json'

# ==================== EMAIL CONFIG ====================
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "reybmziki@gmail.com",
    "smtp_password": "jykv iebr gxam vxlo"
}

# ==================== FUNCTIONS ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_license_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

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
                    "license_expiry": (datetime.now() + timedelta(days=3650)).isoformat(),
                    "reset_token": None,
                    "reset_expiry": None
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
            "license_expiry": (datetime.now() + timedelta(days=3650)).isoformat(),
            "reset_token": None,
            "reset_expiry": None
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

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w') as f:
        json.dump(reviews, f, indent=4)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        "total_bypasses": 0,
        "total_users": 0,
        "monthly_revenue": 0,
        "devices_by_month": {}
    }

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def update_stats(device_count=1, revenue=0):
    stats = load_stats()
    stats["total_bypasses"] += device_count
    current_month = datetime.now().strftime("%Y-%m")
    if current_month not in stats["devices_by_month"]:
        stats["devices_by_month"][current_month] = 0
    stats["devices_by_month"][current_month] += device_count
    stats["monthly_revenue"] += revenue
    save_stats(stats)

# ==================== EMAIL FUNCTIONS ====================
def send_email(to_email, subject, body_html, body_text):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_CONFIG["smtp_email"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["smtp_email"], EMAIL_CONFIG["smtp_password"])
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

def send_registration_email(email, username):
    subject = "🎉 Welcome to EASY TOOL - Registration Received"
    body_html = f"""
    <html><body style="font-family:Arial;">
    <div style="background:linear-gradient(135deg,#10b981,#059669); padding:20px; text-align:center;">
        <h1 style="color:white;">EASY TOOL</h1>
    </div>
    <div style="padding:20px;">
        <h2>Hello {username}!</h2>
        <p>Thank you for registering with EASY TOOL.</p>
        <p>Your account is currently <strong>pending admin approval</strong>.</p>
        <p>You will receive an email once your account is activated.</p>
        <hr>
        <p style="color:#666;">Contact: 254111457171 | Email: reytechfix@gmail.com</p>
    </div>
    </body></html>
    """
    body_text = f"Hello {username}!\n\nThank you for registering. Your account is pending admin approval.\n\nContact: 254111457171"
    return send_email(email, subject, body_html, body_text)

def send_approval_email(email, username, days):
    subject = "✅ Your EASY TOOL Account Has Been Activated!"
    body_html = f"""
    <html><body style="font-family:Arial;">
    <div style="background:linear-gradient(135deg,#10b981,#059669); padding:20px; text-align:center;">
        <h1 style="color:white;">EASY TOOL</h1>
    </div>
    <div style="padding:20px;">
        <h2>Congratulations {username}!</h2>
        <p>Your account has been <strong style="color:#10b981;">ACTIVATED</strong> by admin.</p>
        <p>Your license is valid for <strong>{days} days</strong>.</p>
        <p>You can now login and start using EASY TOOL to bypass MDM locks.</p>
        <div style="background:#f0fdf4; padding:15px; border-radius:10px;">
            <p><strong>Quick Links:</strong></p>
            <p>🔗 Login: https://easyttool-com.onrender.com</p>
            <p>📱 WhatsApp Support: 254111457171</p>
        </div>
        <hr>
        <p style="color:#666;">Contact: 254111457171 | Email: reytechfix@gmail.com</p>
    </div>
    </body></html>
    """
    body_text = f"Congratulations {username}!\n\nYour account has been activated. License valid for {days} days.\n\nLogin: https://easyttool-com.onrender.com"
    return send_email(email, subject, body_html, body_text)

def send_reset_email(email, username, token):
    subject = "🔐 EASY TOOL - Password Reset Request"
    body_html = f"""
    <html><body style="font-family:Arial;">
    <div style="background:linear-gradient(135deg,#ef4444,#dc2626); padding:20px; text-align:center;">
        <h1 style="color:white;">EASY TOOL</h1>
    </div>
    <div style="padding:20px;">
        <h2>Password Reset Request</h2>
        <p>Hello {username},</p>
        <p>We received a request to reset your password.</p>
        <p>Your reset token is: <strong style="font-size:20px; background:#f0fdf4; padding:10px;">{token}</strong></p>
        <p>Enter this token on the login page to reset your password.</p>
        <p>This token expires in <strong>1 hour</strong>.</p>
        <hr>
        <p>If you did not request this, please ignore this email.</p>
    </div>
    </body></html>
    """
    body_text = f"Password Reset Request\n\nYour reset token is: {token}\n\nValid for 1 hour."
    return send_email(email, subject, body_html, body_text)

# ==================== ROUTES ====================
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
        
        for user in users.values():
            if user.get('email') == email:
                return jsonify({'success': False, 'error': 'Email already registered'})
        
        pending[username] = {
            'password': hash_password(password),
            'email': email,
            'registered_at': datetime.now().isoformat()
        }
        save_pending(pending)
        
        # Send email notification
        send_registration_email(email, username)
        
        return jsonify({'success': True, 'message': 'Registration successful! Check your email. Awaiting admin approval.'})
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
        
        # Auto check expiry
        if username != 'REYTECHFX':
            expiry = user.get('license_expiry')
            if expiry and datetime.now() > datetime.fromisoformat(expiry):
                user['is_active'] = False
                save_users(users)
                return jsonify({'success': False, 'error': 'License expired. Please renew.'})
        
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

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        users = load_users()
        username = None
        for u, user in users.items():
            if user.get('email') == email:
                username = u
                break
        
        if not username:
            return jsonify({'success': False, 'error': 'Email not found'})
        
        token = generate_license_key()[:16]
        expiry = datetime.now() + timedelta(hours=1)
        
        users[username]['reset_token'] = token
        users[username]['reset_expiry'] = expiry.isoformat()
        save_users(users)
        
        send_reset_email(email, username, token)
        
        return jsonify({'success': True, 'message': 'Reset token sent to your email'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        users = load_users()
        for username, user in users.items():
            if user.get('reset_token') == token:
                expiry = user.get('reset_expiry')
                if expiry and datetime.now() < datetime.fromisoformat(expiry):
                    users[username]['password'] = hash_password(new_password)
                    users[username]['reset_token'] = None
                    users[username]['reset_expiry'] = None
                    save_users(users)
                    return jsonify({'success': True, 'message': 'Password reset successful!'})
                else:
                    return jsonify({'success': False, 'error': 'Token expired'})
        
        return jsonify({'success': False, 'error': 'Invalid token'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    users = load_users()
    user = users.get(session['username'], {})
    return jsonify({
        'success': True,
        'username': session['username'],
        'email': user.get('email', ''),
        'license_expiry': user.get('license_expiry'),
        'created_at': user.get('created_at', '')
    })

@app.route('/api/user/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    new_email = data.get('email', '').strip()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    users = load_users()
    user = users.get(session['username'])
    
    if new_email:
        # Check if email is taken
        for u, u_data in users.items():
            if u_data.get('email') == new_email and u != session['username']:
                return jsonify({'success': False, 'error': 'Email already in use'})
        user['email'] = new_email
    
    if current_password and new_password:
        if user['password'] != hash_password(current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect'})
        if len(new_password) < 4:
            return jsonify({'success': False, 'error': 'New password must be at least 4 characters'})
        user['password'] = hash_password(new_password)
    
    save_users(users)
    return jsonify({'success': True, 'message': 'Profile updated successfully!'})

@app.route('/api/user/devices', methods=['GET'])
def get_user_devices():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    devices = load_devices()
    user_devices = devices.get(session['username'], [])
    
    users = load_users()
    user = users.get(session['username'], {})
    license_expiry = user.get('license_expiry')
    
    time_remaining = "Unlimited"
    if license_expiry and session['username'] != 'REYTECHFX':
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
    update_stats(device_count=1)
    
    return jsonify({'success': True, 'message': 'Device added successfully!'})

@app.route('/api/user/time_remaining', methods=['GET'])
def get_time_remaining():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    users = load_users()
    user = users.get(session['username'], {})
    license_expiry = user.get('license_expiry')
    
    if not license_expiry or session['username'] == 'REYTECHFX':
        return jsonify({'success': True, 'time_remaining': 'Unlimited', 'days': 9999})
    
    expiry_date = datetime.fromisoformat(license_expiry)
    if datetime.now() > expiry_date:
        return jsonify({'success': True, 'time_remaining': 'Expired', 'days': 0})
    
    days = (expiry_date - datetime.now()).days
    hours = (expiry_date - datetime.now()).seconds // 3600
    
    return jsonify({'success': True, 'time_remaining': f'{days} days {hours} hours', 'days': days})

@app.route('/api/user/reviews', methods=['GET', 'POST'])
def handle_reviews():
    if request.method == 'GET':
        reviews = load_reviews()
        all_reviews = []
        for username, user_reviews in reviews.items():
            for review in user_reviews:
                review['username'] = username
                all_reviews.append(review)
        return jsonify({'success': True, 'reviews': all_reviews[-20:]})  # Last 20 reviews
    
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    data = request.json
    rating = data.get('rating', 0)
    comment = data.get('comment', '').strip()
    
    if rating < 1 or rating > 5:
        return jsonify({'success': False, 'error': 'Rating must be 1-5'})
    if not comment:
        return jsonify({'success': False, 'error': 'Comment is required'})
    
    reviews = load_reviews()
    if session['username'] not in reviews:
        reviews[session['username']] = []
    
    reviews[session['username']].append({
        'rating': rating,
        'comment': comment,
        'date': datetime.now().isoformat()
    })
    
    save_reviews(reviews)
    return jsonify({'success': True, 'message': 'Review added!'})

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
    duration = int(data.get('duration', 30))
    
    pending = load_pending()
    users = load_users()
    
    if username not in pending:
        return jsonify({'success': False, 'error': 'User not found'})
    
    user_data = pending[username]
    expiry_date = datetime.now() + timedelta(days=duration)
    
    # Calculate price
    if duration == 30:
        price = 20
    elif duration == 90:
        price = 30
    elif duration == 180:
        price = 40
    else:
        price = 60
    
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
    update_stats(revenue=price)
    
    # Send approval email
    send_approval_email(user_data['email'], username, duration)
    
    return jsonify({'success': True, 'message': f'User {username} approved for {duration} days! Email sent.'})

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

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    stats = load_stats()
    users = load_users()
    devices = load_devices()
    
    total_devices = sum(len(d) for d in devices.values())
    active_users = sum(1 for u in users.values() if u.get('is_active', False))
    
    return jsonify({
        'success': True,
        'total_bypasses': stats.get('total_bypasses', 0),
        'total_users': len(users),
        'active_users': active_users,
        'total_devices': total_devices,
        'monthly_revenue': stats.get('monthly_revenue', 0),
        'devices_by_month': stats.get('devices_by_month', {})
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
