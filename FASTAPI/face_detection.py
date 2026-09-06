from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse
from contextlib import asynccontextmanager
import cv2
import time
import uvicorn
import numpy as np
import os
from threading import Lock

camera = None


@asynccontextmanager
async def lifespan(app):
    global camera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    yield
    if camera is not None:
        camera.release()


app = FastAPI(lifespan=lifespan)

# Load the Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_detection_lock = Lock()

# Detect faces in a grayscale image
def detect_faces_in_gray(gray):
    with face_detection_lock:
        # Use the Haar Cascade to detect faces in the grayscale image with adjusted parameters for better detection
        # scaleFactor: 1.1 (slightly smaller scale factor for better detection)
        # minNeighbors: 8 (more neighbors for better detection)
        # minSize: (30, 30) (minimum size of the face to be detected)
        # flags: cv2.CASCADE_SCALE_IMAGE (scale the image for better detection)
        return face_cascade.detectMultiScale(gray, 
                                             scaleFactor=1.1, 
                                             minNeighbors=8, 
                                             minSize=(30, 30), 
                                             flags=cv2.CASCADE_SCALE_IMAGE)

def gen_frames():
    if camera is None or not camera.isOpened():
        return

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces_in_gray(gray)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Live Face Detection</title>
        </head>
        <body>
            <h1>Live Face Detection</h1>
            <img src="/video" width="640" height="480" />
        </body>
    </html>
    """

@app.get("/video")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/detect-faces/")
async def detect_faces(file: UploadFile = File(...), save: bool = True):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return JSONResponse(status_code=400, content={"error": "Invalid image"})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detect_faces_in_gray(gray)

    face_list = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]
    output_path = None
    if save:
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        output_path = f"LOCAL/FACE_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        cv2.imwrite(output_path, img)
    return {"image_path": output_path, "num_faces": len(face_list), "faces": face_list}

@app.get("/favicon.ico")
async def favicon():
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTMLResponse(content="", status_code=204)

@app.get("/health")
async def health_check():
    if camera is None or not camera.isOpened():
        return JSONResponse(status_code=503, content={"status": "Camera not available"})
    return JSONResponse(status_code=200, content={"status": "OK"})
# DO NOT run this directly when using --reload
# Instead, launch with: uvicorn face_detection:app --reload --port 8800
if __name__ == "__main__":
    uvicorn.run("face_detection:app", host="127.0.0.1", port=8800, reload=True)
