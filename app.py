from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ── EAR helpers ──────────────────────────────────────────────
def euclidean(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def eye_aspect_ratio(eye_points):
    A = euclidean(eye_points[1], eye_points[5])
    B = euclidean(eye_points[2], eye_points[4])
    C = euclidean(eye_points[0], eye_points[3])
    return (A + B) / (2.0 * C) if C != 0 else 0

# ── Database ─────────────────────────────────────────────────
DB_PATH = "drowsiness_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS drowsiness_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            status    TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Table ready.")

def log_event(status):
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute(
        "INSERT INTO drowsiness_log (status, timestamp) VALUES (?, ?)",
        (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, status, timestamp FROM drowsiness_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ── Cascades ─────────────────────────────────────────────────
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# ── State ────────────────────────────────────────────────────
EAR_THRESHOLD      = 0.25
CONSEC_FRAMES      = 20
frame_counter      = 0
current_status     = "Awake"
last_logged_status = None

# ── Video stream ─────────────────────────────────────────────
def generate_frames():
    global frame_counter, current_status, last_logged_status

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()
        if not success:
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        eyes_detected = False

        for (fx, fy, fw, fh) in faces:
            cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (0, 200, 255), 2)
            roi_gray  = gray[fy:fy+fh//2, fx:fx+fw]
            roi_color = frame[fy:fy+fh//2, fx:fx+fw]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5, minSize=(20, 20))

            if len(eyes) >= 2:
                eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    cx, cy   = ex+ew//2, ey+eh//2
                    hw, hh   = ew//2, eh//2
                    eye_pts  = [
                        (cx-hw, cy), (cx-hw//2, cy-hh), (cx+hw//2, cy-hh),
                        (cx+hw, cy), (cx+hw//2, cy+hh), (cx-hw//2, cy+hh),
                    ]
                    if eye_aspect_ratio(eye_pts) < EAR_THRESHOLD:
                        frame_counter += 1
                    else:
                        frame_counter = 0

        if not eyes_detected:
            frame_counter += 1

        current_status = "Drowsy" if frame_counter >= CONSEC_FRAMES else "Awake"

        if current_status != last_logged_status:
            log_event(current_status)
            last_logged_status = current_status

        color = (0, 255, 80) if current_status == "Awake" else (0, 0, 255)
        cv2.putText(frame, f"Status: {current_status}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        if current_status == "Drowsy":
            cv2.putText(frame, "!! DROWSINESS ALERT !!", (60, frame.shape[0]-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    cap.release()

# ── Routes ───────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status():
    return jsonify({"status": current_status})

@app.route("/logs")
def logs():
    rows = get_recent_logs(10)
    return jsonify([{"id": r[0], "status": r[1], "timestamp": r[2]} for r in rows])

# ── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("[INFO] Starting Drowsiness Detection...")
    print("[INFO] Open http://127.0.0.1:5001 in your browser")
    app.run(debug=False, threaded=True, port=5001)
