from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ==================== ADD THIS ROUTE ====================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "EASY TOOL API is running!",
        "version": "0.02",
        "endpoints": {
            "/": "Home page",
            "/api/check_adb": "Check ADB devices",
            "/api/run_command": "Run ADB command",
            "/api/login": "Login endpoint"
        }
    })

# Your other routes...
@app.route('/api/check_adb')
def check_adb():
    # Your code here
    return jsonify({"status": "ok"})

# ==================== END ====================

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
