@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/status")
def api_status():
    return jsonify({
        "message": "EASY TOOL API is running!",
        "status": "online",
        "version": "0.02"
    })
