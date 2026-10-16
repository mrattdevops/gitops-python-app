
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "application": "gitops-advanced-app",
        "message": "Hello from Advanced GitOps Lab",
        "version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("APP_ENV", "local")
    })


@app.get("/health/live")
def liveness():
    return jsonify({"status": "alive"}), 200


@app.get("/health/ready")
def readiness():
    return jsonify({"status": "ready"}), 200


@app.get("/api/info")
def info():
    return jsonify({
        "hostname": socket.gethostname(),
        "environment": os.getenv("APP_ENV", "local"),
        "version": os.getenv("APP_VERSION", "dev")
    })

@app.get("/api/load")
def cpu_load():
    total = 0

    for i in range(500_000):
        total += (i * i) % 97

    return jsonify({
        "status": "completed",
        "result": total,
        "hostname": socket.gethostname()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
