
import os
import socket

from flask import Flask, jsonify

import application_config

app = Flask(__name__)


@app.errorhandler(application_config.ConfigurationError)
def configuration_error(_error):
    return jsonify({"error": "Application configuration is unavailable."}), 503


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
    application_config.get_application_config()
    return jsonify({"status": "ready"}), 200


@app.get("/api/info")
def info():
    config = application_config.get_application_config()

    return jsonify({
        "hostname": socket.gethostname(),
        "environment": config.get(
            "APP_ENV",
            os.getenv("APP_ENV", "local")
        ),
        "version": os.getenv("APP_VERSION", "dev"),
        "vault_config_loaded": application_config.CONFIG_FILE.is_file()
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
