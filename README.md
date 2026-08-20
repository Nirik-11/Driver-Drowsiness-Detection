# Driver Drowsiness Detection System

A real-time **Driver Drowsiness Detection System** built using **Python, Flask, and OpenCV**. The system monitors the driver's eyes using the **Eye Aspect Ratio (EAR)** and detects prolonged eye closure, triggering an alert when signs of drowsiness are identified.

## Features

* Real-time eye tracking using OpenCV
* Eye Aspect Ratio (EAR) based drowsiness detection
* Automatic alert when prolonged eye closure is detected
* Web-based interface using Flask
* Session and alert logging using SQLite
* `/status` endpoint to check the current drowsiness status
* `/logs` endpoint to retrieve recent detection logs

## Tech Stack

* **Programming Language:** Python
* **Backend:** Flask
* **Computer Vision:** OpenCV
* **Database:** SQLite
* **Frontend:** HTML, CSS
* **Detection Method:** Eye Aspect Ratio (EAR)

## How It Works

1. The webcam captures the driver's video in real time.
2. OpenCV processes the video frames to detect the driver's eyes.
3. The **Eye Aspect Ratio (EAR)** is calculated for each frame.
4. When the EAR falls below a predefined threshold for a sustained period, the system identifies the driver as drowsy.
5. An alert is triggered to warn the driver.
6. Detection events are stored in the SQLite database with timestamps.

## Project Structure

```text
Driver-Drowsiness-Detection/
│
├── app.py
├── requirements.txt
├── drowsiness_log.db
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Nirik-11/Driver-Drowsiness-Detection.git
cd Driver-Drowsiness-Detection
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Open:

```text
http://127.0.0.1:5001
```

Make sure your computer has a working webcam.

## Database

The project uses **SQLite** to store drowsiness detection events and alert logs.

Each detection event can include information such as:

* Detection status
* Timestamp
* Alert information

## Important Note

This project is designed primarily for **local execution** because webcam capture and OpenCV processing are performed on the server side.

For cloud deployment, webcam access would need to be handled on the client side using browser-based camera APIs, with video frames sent to the server for processing.

## Future Improvements

* Add sound and voice alerts
* Improve facial landmark detection
* Add yawning detection
* Add head-pose estimation
* Store detailed driver session analytics
* Create a real-time dashboard for detection statistics
* Support client-side webcam streaming for cloud deployment


LinkedIn: https://www.linkedin.com/in/nirikreddy/
