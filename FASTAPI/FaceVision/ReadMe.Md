# FaceVision — FastAPI Face Detection API

A modular **FastAPI-based face detection application** using **OpenCV Haar Cascade**, with JWT authentication, protected API endpoints, webcam streaming, image upload/detection, a web dashboard, automated tests, and Locust-based load testing.

---

## Features

* FastAPI REST API
* JWT-based authentication
* Role-based access (`admin` / `user`)
* Login through a popup/modal on the home page
* Protected dashboard
* Live webcam video streaming
* Face detection using OpenCV Haar Cascade
* Face detection from uploaded images
* Automatic saving of detected images
* Protected image access
* Application and face-detection logging
* Automated testing with `pytest`
* Load testing with `Locust`
* Configurable authentication through `.env`
* JWT tokens are not exposed in application logs

---

## Project Structure

```text
FASTAPI/
│
├── main.py
├── auth.py
├── face_detection.py
├── run.py
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── home.html
│   ├── login.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── dashboard.js
│       └── home.js
│
├── LOCAL/
│   └── detected/
│
├── logs/
│
└── Testing/
    ├── test_auth.py
    ├── test_api.py
    ├── test_face_detection.py
    └── locustfile.py
```

---

# Architecture

The application is divided into separate modules:

```text
                    ┌─────────────────────┐
                    │      Browser        │
                    │                     │
                    │ Home / Dashboard    │
                    └──────────┬──────────┘
                               │
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      main.py        │
                    └───────┬─────┬───────┘
                            │     │
                 ┌──────────┘     └──────────┐
                 ▼                           ▼
        ┌─────────────────┐         ┌──────────────────┐
        │    auth.py      │         │ face_detection.py│
        │                 │         │                  │
        │ JWT             │         │ OpenCV           │
        │ Authentication  │         │ Haar Cascade     │
        │ Authorization   │         │ Face Detection   │
        └─────────────────┘         └──────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ LOCAL/detected/ │
                                    │ Detected Images │
                                    └─────────────────┘
```

---

# Requirements

## System

Recommended environment:

* Ubuntu/Linux
* Python 3.10+
* Webcam for live detection
* OpenCV-compatible environment

Check Python:

```bash
python --version
```

Example:

```text
Python 3.12.3
```

---

# Installation

## 1. Clone the project

```bash
git clone <your-repository-url>
cd FASTAPI
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

You should see something similar to:

```text
(.venv) user@machine:~/Development/MLOps/FASTAPI$
```

---

## 3. Install dependencies

Install the required packages:

```bash
pip install fastapi uvicorn python-multipart python-jose[cryptography] python-dotenv opencv-python numpy pytest locust
```

Alternatively, if a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=replace_this_with_a_long_random_secret
JWT_ALGORITHM=HS256
JWT_TOKEN_EXPIRE_MINUTES=30

AUTH_ADMIN_USERNAME=admin
AUTH_ADMIN_PASSWORD=your_admin_password
AUTH_ADMIN_ROLE=admin

AUTH_USER_USERNAME=pawankrgunjan
AUTH_USER_PASSWORD=your_user_password
AUTH_USER_ROLE=user
```

---

## Generate a secure JWT secret

Do not use a simple secret in production.

Generate one using:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the generated value into:

```env
JWT_SECRET_KEY=YOUR_GENERATED_SECRET
```

---

## Protect `.env`

```bash
chmod 600 .env
```

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.pyc
logs/
```

Never commit passwords or JWT secrets to Git.

---

# Running the Application

There are two recommended ways to start the application.

## Option 1 — Using `run.py`

If `run.py` contains the Uvicorn configuration:

```bash
python run.py
```

Recommended configuration:

```python
import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        access_log=False,
        log_level="info",
    )
```

---

## Option 2 — Using Uvicorn directly

```bash
uvicorn main:app \
    --reload \
    --host 127.0.0.1 \
    --port 8000 \
    --no-access-log
```

The `--no-access-log` option is important because the application uses JWT tokens in the URL.

---

# Application URLs

Once the application is running:

### Home

```text
http://127.0.0.1:8000/
```

### Health

```text
http://127.0.0.1:8000/health
```

### Detector status

```text
http://127.0.0.1:8000/detector-status
```

### API documentation

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# Authentication

The application uses JWT authentication.

The login form is displayed as a popup on the home page.

```text
Home
 │
 └── Sign In
       │
       ▼
   Login Modal
       │
       ▼
    POST /login
       │
       ▼
   JWT Access Token
       │
       ▼
   Protected Dashboard
```

The frontend sends:

```http
POST /login
Content-Type: application/x-www-form-urlencoded
```

with:

```text
username=<username>
password=<password>
```

A successful response contains:

```json
{
    "access_token": "<JWT>",
    "token_type": "bearer",
    "username": "username",
    "role": "user"
}
```

The browser then redirects to:

```text
/<JWT>
```

---

# Protected Routes

After authentication, the JWT is used as the URL token.

### Dashboard

```text
/<token>
```

### Live video

```text
/<token>/video
```

### Face detection

```text
/<token>/detect-faces/
```

### Detected image

```text
/<token>/images/{filename}
```

The token is validated before accessing protected resources.

---

# Face Detection

The application uses OpenCV's Haar Cascade classifier.

The main functionality is implemented in:

```text
face_detection.py
```

The detector supports:

* Image loading
* Image decoding
* Face detection
* Drawing bounding boxes
* Image processing
* Saving processed images
* Frame processing
* Webcam streaming

---

## Face Detection Flow

```text
Input Image
     │
     ▼
Decode / Read Image
     │
     ▼
Convert BGR → Grayscale
     │
     ▼
Haar Cascade Detection
     │
     ▼
Detected Faces
     │
     ▼
Draw Bounding Boxes
     │
     ▼
Save / Return Processed Image
```

---

# Upload Face Detection

The API accepts an image using multipart form data.

Example:

```bash
curl -X POST \
    -F "file=@LOCAL/FACE_2026-09-06_06-30-25.jpg" \
    http://127.0.0.1:8000/<TOKEN>/detect-faces/
```

Replace `<TOKEN>` with a valid JWT.

The processed image is saved under:

```text
LOCAL/detected/
```

---

# Webcam Detection

The dashboard can display the live webcam stream.

Endpoint:

```text
/<token>/video
```

The backend generates an MJPEG stream using OpenCV.

The general flow is:

```text
Webcam
   │
   ▼
OpenCV VideoCapture
   │
   ▼
Capture Frame
   │
   ▼
Face Detection
   │
   ▼
Draw Bounding Boxes
   │
   ▼
JPEG Encode
   │
   ▼
MJPEG HTTP Stream
   │
   ▼
Browser
```

A webcam must be available to the machine running the application.

---

# Logging

The application writes logs to:

```text
logs/
```

Typical logs include:

```text
logs/app.log
logs/face_detection.log
```

The application is configured to avoid logging JWT tokens.

For example, instead of logging:

```text
GET /eyJhbGciOiJIUzI1NiIs...
```

the application sanitizes the URL and logs:

```text
GET /<TOKEN>
```

This is especially important because JWTs are present in the URL path.

---

# Testing

The project uses `pytest`.

Run all tests:

```bash
pytest -v
```

---

## Authentication Tests

```bash
pytest -v Testing/test_auth.py
```

These tests cover:

* JWT creation
* JWT validation
* User authentication
* Admin authentication
* User roles
* Permissions
* Expired tokens
* Invalid tokens
* Tampered tokens

---

## Face Detection Tests

```bash
pytest -v Testing/test_face_detection.py
```

The face detection tests cover:

* Detector initialization
* Haar cascade loading
* Face detection
* Face coordinate validation
* Drawing detected faces
* Image decoding
* Image reading
* Image saving
* Image processing
* Frame processing
* Detector status
* Camera helper functions
* Detected-image directory

The test image used by the suite is:

```text
LOCAL/FACE_2026-09-06_06-30-25.jpg
```

If this image does not exist, relevant tests are skipped.

---

## API Tests

Run:

```bash
pytest -v Testing/test_api.py
```

These tests should be run with the FastAPI application available if they make HTTP requests against the running application.

---

# Load Testing

The project uses **Locust** for API load testing.

The Locust configuration is:

```text
Testing/locustfile.py
```

It tests:

* Login
* Health endpoint
* Detector status
* Dashboard
* Webcam endpoint
* Face detection
* Protected endpoints
* Rate-limit behavior

---

# Starting the Application for Locust

First start FastAPI:

```bash
python run.py
```

Verify:

```bash
curl -i http://127.0.0.1:8000/health
```

Expected response should be HTTP `200`.

---

# Starting Locust

From the project root:

```bash
locust \
    -f Testing/locustfile.py \
    --host http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8089
```

---

# Locust Test Configuration

Start with a small number of users.

Recommended progression:

```text
2 users
   ↓
10 users
   ↓
20 users
   ↓
50 users
   ↓
100 users
```

Do not immediately jump to very high concurrency if face detection is CPU-intensive.

---

## Headless Load Test

Example:

```bash
locust \
    -f Testing/locustfile.py \
    --host http://127.0.0.1:8000 \
    --headless \
    -u 10 \
    -r 2 \
    -t 60s
```

Parameters:

```text
-u 10
```

Number of users.

```text
-r 2
```

Users spawned per second.

```text
-t 60s
```

Test duration.

---

# Rate Limit Testing

The Locust test includes requests intended to observe HTTP `429 Too Many Requests`.

A `429` response means the API has rejected a request because a configured rate limit has been exceeded.

However, a normal load test does **not necessarily prove that a rate limit exists or determine its exact threshold**.

For accurate rate-limit testing, use a dedicated burst test that sends requests rapidly.

Example test progression:

```text
10 requests/sec
       ↓
25 requests/sec
       ↓
50 requests/sec
       ↓
100 requests/sec
       ↓
200 requests/sec
```

Monitor the number of:

```text
HTTP 429
```

responses.

---

# Performance Metrics

Locust provides:

* Number of requests
* Number of failures
* Average response time
* Minimum response time
* Maximum response time
* Median response time
* Requests per second
* Failure percentage
* Percentile latency

Important percentiles:

```text
P50
P90
P95
P99
```

For example:

```text
P95 = 8900 ms
```

means approximately 95% of requests completed within 8.9 seconds.

---

# Performance Considerations

Face detection is CPU-intensive compared with simple endpoints such as:

```text
/health
/detector-status
```

During load testing, monitor system resources:

```bash
htop
```

Memory:

```bash
free -h
```

System load:

```bash
uptime
```

Disk:

```bash
df -h
```

Because Locust and FastAPI may be running on the same machine, heavy Locust traffic can affect the API's response times.

For production benchmarking, it is better to run:

```text
Load Generator
      │
      │ HTTP
      ▼
API Server
      │
      ▼
Face Detection
```

on separate machines or containers.

---

# Security Considerations

This project currently uses JWTs in the URL:

```text
/<JWT>
```

This is acceptable for development/testing but is **not recommended for production**.

URLs can potentially appear in:

* Browser history
* Reverse-proxy logs
* Access logs
* Monitoring systems
* Referrer information
* Screenshots
* Analytics systems

A production implementation should preferably use:

```http
Authorization: Bearer <JWT>
```

or a secure, HTTP-only cookie.

---

## Additional Security Recommendations

For production:

* Use HTTPS.
* Store JWT secrets securely.
* Never commit `.env`.
* Hash passwords instead of storing plaintext passwords.
* Use short-lived access tokens.
* Consider refresh tokens.
* Implement proper logout/token revocation where required.
* Add rate limiting.
* Validate uploaded files.
* Limit upload size.
* Restrict CORS.
* Disable debug mode.
* Use a production ASGI deployment.
* Avoid exposing sensitive information in logs.

---

# Troubleshooting

## Application does not start

Check:

```bash
python --version
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Port 8000 already in use

Check:

```bash
ss -ltnp | grep 8000
```

or:

```bash
lsof -i :8000
```

Stop the existing process if required.

---

## Webcam does not work

Check that a camera exists:

```bash
ls /dev/video*
```

You should see something like:

```text
/dev/video0
```

You can also test the camera using an operating-system camera application.

---

## Face detection returns no faces

Make sure the image:

* Contains a visible face.
* Has reasonable lighting.
* Has sufficient resolution.
* Is a supported image format.
* Is loaded correctly by OpenCV.

The project test image is:

```text
LOCAL/FACE_2026-09-06_06-30-25.jpg
```

---

## Tests fail because the test image is missing

Check:

```bash
ls -lh LOCAL/FACE_2026-09-06_06-30-25.jpg
```

The expected location is:

```text
FASTAPI/
└── LOCAL/
    └── FACE_2026-09-06_06-30-25.jpg
```

---

## Locust shows zero requests

First verify that the FastAPI server is running:

```bash
curl -i http://127.0.0.1:8000/health
```

Then start Locust:

```bash
locust \
    -f Testing/locustfile.py \
    --host http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8089
```

Start with:

```text
Users: 2
Spawn rate: 1
```

and increase gradually.

---

## Locust reports HTTP 500

Check the FastAPI logs:

```bash
tail -f logs/*.log
```

Also monitor:

```bash
htop
```

and:

```bash
free -h
```

Face detection failures should be investigated before increasing concurrency significantly.

---

# Development Workflow

Recommended development workflow:

```text
1. Activate virtual environment
          │
          ▼
2. Start FastAPI
          │
          ▼
3. Test /health
          │
          ▼
4. Run pytest
          │
          ▼
5. Test manually in browser
          │
          ▼
6. Run Locust with 2 users
          │
          ▼
7. Increase load gradually
          │
          ▼
8. Analyze latency/errors
```

Commands:

```bash
source .venv/bin/activate
```

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```bash
curl -i http://127.0.0.1:8000/health
```

```bash
pytest -v
```

```bash
locust -f Testing/locustfile.py --host http://127.0.0.1:8000
```


---

# API Summary

| Method | Endpoint                     | Authentication | Purpose                        |
| ------ | ---------------------------- | -------------: | ------------------------------ |
| GET    | `/`                          |             No | Home page                      |
| GET    | `/health`                    |             No | Application health             |
| GET    | `/detector-status`           |             No | Face detector status           |
| POST   | `/login`                     |             No | Authenticate user              |
| GET    | `/{token}`                   |            JWT | Dashboard                      |
| GET    | `/{token}/video`             |            JWT | Live webcam stream             |
| POST   | `/{token}/detect-faces/`     |            JWT | Detect faces in uploaded image |
| GET    | `/{token}/images/{filename}` |            JWT | Access detected image          |

---

# Technologies

* **Python**
* **FastAPI**
* **Uvicorn**
* **OpenCV**
* **NumPy**
* **JWT**
* **python-dotenv**
* **Pytest**
* **Locust**
* **HTML/CSS/JavaScript**

---

# Future Improvements

Potential improvements for the next version:

* Replace Haar Cascade with a modern deep-learning face detector.
* Add password hashing with Argon2 or bcrypt.
* Move JWT from URL paths to HTTP Authorization headers.
* Add refresh-token support.
* Add proper API rate limiting.
* Add request size limits.
* Add image type validation.
* Add asynchronous/background processing for expensive detection jobs.
* Add multiple-worker deployment.
* Add Docker support.
* Add CI/CD with automated pytest execution.
* Add Prometheus metrics.
* Add structured JSON logging.
* Add dedicated performance-testing environments.
* Add face recognition in addition to face detection.

---

# License

Add your preferred license here.

Example:

```text
MIT License
```

---

# Author

**Pawan Gunjan**

FaceVision — FastAPI-based face detection and API load-testing project.


