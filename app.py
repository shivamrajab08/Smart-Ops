import ipaddress
import os
import time
from urllib.parse import urlparse
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPO = "ratnakargupta02-byte/Smart-Ops"


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/status")
def status():
    return jsonify({
        "application": "Smart Ops",
        "status": "running",
        "health": "healthy",
        "deployment_platform": "Render",
        "container_platform": "Docker"
    })


@app.route("/api/deployments")
def deployments():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10
        )
        response.raise_for_status()

        commits = response.json()[:10]
        history = []

        for commit in commits:
            history.append({
                "message": commit["commit"]["message"],
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "url": commit["html_url"]
            })

        return jsonify({
            "repository": GITHUB_REPO,
            "total": len(history),
            "deployments": history
        })

    except requests.RequestException:
        return jsonify({
            "error": "Unable to fetch GitHub history"
        }), 502


def is_safe_url(target_url: str):
    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        return False, "Invalid protocol. Only http:// and https:// are supported."
    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: missing host."

    lowered = hostname.lower()
    if lowered in ("localhost", "0.0.0.0", "127.0.0.1", "::1") or lowered.endswith((".local", ".internal")):
        return False, "Access to localhost or internal network addresses is blocked for security."

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_link_local:
            return False, "Access to private or local IP ranges is blocked for security."
    except ValueError:
        pass

    return True, None


@app.route("/api/test-service", methods=["POST"])
def test_service():
    payload = request.get_json(silent=True) or {}
    raw_url = payload.get("url", "").strip()
    method = str(payload.get("method", "GET")).upper().strip()

    if not raw_url:
        return jsonify({
            "success": False,
            "error": "URL parameter is required."
        }), 400

    allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
    if method not in allowed_methods:
        return jsonify({
            "success": False,
            "error": f"Invalid HTTP method. Allowed: {', '.join(sorted(allowed_methods))}"
        }), 400

    try:
        expected_status = int(payload.get("expected_status", 200))
    except (ValueError, TypeError):
        expected_status = 200

    is_safe, error_msg = is_safe_url(raw_url)
    if not is_safe:
        return jsonify({
            "success": False,
            "error": error_msg
        }), 400

    start_time = time.time()
    try:
        response = requests.request(
            method=method,
            url=raw_url,
            timeout=8,
            headers={
                "User-Agent": "Smart-Ops-Testing-Engine/1.0",
                "Accept": "*/*"
            }
        )
        latency_ms = round((time.time() - start_time) * 1000, 2)
        passed = (response.status_code == expected_status)
        preview = response.text[:300] if response.text else ""

        return jsonify({
            "success": True,
            "passed": passed,
            "url": raw_url,
            "method": method,
            "status_code": response.status_code,
            "status_text": response.reason,
            "expected_status": expected_status,
            "latency_ms": latency_ms,
            "content_type": response.headers.get("Content-Type", "Unknown"),
            "response_size_bytes": len(response.content),
            "response_preview": preview
        }), 200

    except requests.exceptions.Timeout:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "passed": False,
            "url": raw_url,
            "method": method,
            "latency_ms": latency_ms,
            "error": "Request timed out (server took longer than 8 seconds to respond)."
        }), 504

    except requests.exceptions.SSLError as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "passed": False,
            "url": raw_url,
            "method": method,
            "latency_ms": latency_ms,
            "error": f"SSL/TLS Certificate verification failed: {str(e)}"
        }), 502

    except requests.exceptions.ConnectionError:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "passed": False,
            "url": raw_url,
            "method": method,
            "latency_ms": latency_ms,
            "error": "Failed to establish connection. Target host might be down or unreachable."
        }), 502

    except requests.exceptions.RequestException as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return jsonify({
            "success": False,
            "passed": False,
            "url": raw_url,
            "method": method,
            "latency_ms": latency_ms,
            "error": f"Request failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
