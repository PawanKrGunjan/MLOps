from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

import uvicorn
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    Form,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from auth import USERS, create_access_token, require_permission
from face_detection import (
    DETECTED_DIR as FACE_DETECTED_DIR,
    face_detector,
    generate_frames,
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
LOCAL_DIR = BASE_DIR / "LOCAL"
LOGS_DIR = BASE_DIR / "logs"

DETECTED_DIR = LOCAL_DIR / "detected"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOCAL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DETECTED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("app")

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Prevent duplicate logging through the root logger.
    logger.propagate = False


# ============================================================
# JWT PATH REDACTION
# ============================================================

JWT_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"
)


def sanitize_path(path: str) -> str:
    """
    Remove JWT tokens from URL paths before logging.

    Example:

        /eyJhbGciOiJIUzI1NiIs.../video

    becomes:

        /<TOKEN>/video
    """

    if not path:
        return "/"

    parts = path.strip("/").split("/")

    if not parts:
        return "/"

    first_part = parts[0]

    if JWT_PATTERN.fullmatch(first_part):

        parts[0] = "<TOKEN>"

    sanitized = "/" + "/".join(parts)

    if path.endswith("/") and sanitized != "/":

        sanitized += "/"

    return sanitized


# ============================================================
# ACCESS LOG MIDDLEWARE
# ============================================================

class RedactTokenMiddleware(BaseHTTPMiddleware):
    """
    Application-level access logger.

    JWT tokens are removed from URL paths before
    writing anything to the application log.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        response = None

        try:

            response = await call_next(request)

            return response

        finally:

            safe_path = sanitize_path(
                request.url.path
            )

            status_code = (
                response.status_code
                if response is not None
                else 500
            )

            logger.info(
                "%s %s HTTP/%s %s",
                request.method,
                safe_path,
                request.scope.get(
                    "http_version",
                    "1.1",
                ),
                status_code,
            )


# ============================================================
# FASTAPI LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle handler.

    Startup code runs before yield.
    Shutdown code runs after yield.

    This replaces the deprecated:

        @app.on_event("startup")
        @app.on_event("shutdown")
    """

    # --------------------------------------------------------
    # STARTUP
    # --------------------------------------------------------

    logger.info(
        "=================================================="
    )

    logger.info(
        "Face Detection API starting"
    )

    logger.info(
        "Base directory: %s",
        BASE_DIR,
    )

    logger.info(
        "Templates directory: %s",
        TEMPLATES_DIR,
    )

    logger.info(
        "Static directory: %s",
        STATIC_DIR,
    )

    logger.info(
        "Detected images directory: %s",
        DETECTED_DIR,
    )

    logger.info(
        "OpenCV detector initialized=%s",
        (
            face_detector.face_cascade is not None
            and not face_detector.face_cascade.empty()
        ),
    )

    logger.info(
        "JWT redaction logging enabled"
    )

    logger.info(
        "Uvicorn access logging should be disabled "
        "to prevent JWT exposure"
    )

    logger.info(
        "=================================================="
    )

    # --------------------------------------------------------
    # APPLICATION RUNS
    # --------------------------------------------------------

    yield

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    logger.info(
        "Face Detection API shutting down"
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Face Detection API",
    description=(
        "JWT protected OpenCV face detection application"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# MIDDLEWARE
# ============================================================

app.add_middleware(
    RedactTokenMiddleware
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# STATIC FILES
# ============================================================

if STATIC_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(
            directory=str(STATIC_DIR)
        ),
        name="static",
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_authenticated_user(
    token: str,
) -> dict:
    """
    Validate JWT and allow both admin and user roles.
    """

    return require_permission(
        token,
        ["admin", "user"],
    )


def validate_filename(
    filename: str,
) -> str:
    """
    Prevent path traversal when accessing
    detected images.
    """

    safe_filename = Path(filename).name

    if safe_filename != filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    if not safe_filename:

        raise HTTPException(
            status_code=400,
            detail="Filename cannot be empty",
        )

    return safe_filename


def face_detector_status() -> dict:
    """
    Internal detector status helper.
    """

    return {
        "status": "ok",
        "detector": "opencv_haar_cascade",
        "cascade_loaded": (
            face_detector.face_cascade is not None
            and not face_detector.face_cascade.empty()
        ),
    }


# ============================================================
# PUBLIC HOME PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):
    """
    Public landing page.

    Login is expected to be displayed as a
    popup/modal from this page.
    """

    logger.info(
        "Public home page requested"
    )

    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    user = USERS.get(username)

    if not user or user["password"] != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(
        username=username,
        role=user["role"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": username,
        "role": user["role"],
    }


# ============================================================
# FAVICON
# ============================================================

@app.get(
    "/favicon.ico",
)
async def favicon():
    """
    Prevent /favicon.ico from being interpreted as a JWT.
    """

    favicon_path = (
        STATIC_DIR / "favicon.ico"
    )

    if favicon_path.exists():

        return FileResponse(
            favicon_path
        )

    return HTMLResponse(
        content="",
        status_code=204,
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
)
async def health():
    """
    Application health check.
    """

    return {
        "status": "ok",
        "service": "face_detection",
        "detector": "opencv",
    }


# ============================================================
# DETECTOR STATUS
# ============================================================

@app.get(
    "/detector-status",
)
async def detector_status():
    """
    Return OpenCV detector status.
    """

    return face_detector_status()


# ============================================================
# AUTHENTICATED DASHBOARD
# ============================================================

@app.get(
    "/{token}",
    response_class=HTMLResponse,
)
async def authenticated_home(
    request: Request,
    token: str,
):
    """
    JWT-protected dashboard.

    URL:

        /<JWT>
    """

    user = get_authenticated_user(
        token
    )

    username = str(
        user.get(
            "username",
            "User",
        )
    )

    role = str(
        user.get(
            "role",
            "unknown",
        )
    )

    logger.info(
        "Dashboard accessed username=%s role=%s",
        username,
        role,
    )

    response = templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "token": token,
            "username": username,
            "role": role,
        },
    )

    # Never cache a page containing the JWT.
    response.headers[
        "Cache-Control"
    ] = "no-store"

    response.headers[
        "Pragma"
    ] = "no-cache"

    response.headers[
        "Expires"
    ] = "0"

    return response


# ============================================================
# LIVE CAMERA
# ============================================================

@app.get(
    "/{token}/video",
)
async def video_feed(
    token: str,
):
    """
    JWT-protected live webcam feed.

    URL:

        /<JWT>/video
    """

    user = get_authenticated_user(
        token
    )

    logger.info(
        "Camera stream requested username=%s role=%s",
        user["username"],
        user["role"],
    )

    return StreamingResponse(
        generate_frames(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


# ============================================================
# FACE DETECTION
# ============================================================

@app.post(
    "/{token}/detect-faces/",
)
async def detect_faces(
    token: str,
    file: UploadFile = File(...),
    save_result: bool = True,
):
    """
    Detect faces in an uploaded image.

    URL:

        POST /<JWT>/detect-faces/

    Supported formats:

        JPG
        JPEG
        PNG
        WEBP
    """

    user = get_authenticated_user(
        token
    )

    username = user["username"]
    role = user["role"]

    # Never log the JWT.
    # Only the sanitized filename is logged.

    filename = (
        file.filename or ""
    )

    safe_log_filename = (
        Path(filename).name
        if filename
        else "unknown"
    )

    logger.info(
        "Face detection requested "
        "username=%s role=%s filename=%s",
        username,
        role,
        safe_log_filename,
    )

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    if extension not in allowed_extensions:

        logger.warning(
            "Unsupported image format "
            "username=%s extension=%s",
            username,
            extension,
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG or WEBP."
            ),
        )

    # --------------------------------------------------------
    # Read uploaded image
    # --------------------------------------------------------

    try:

        image_bytes = await file.read()

    except Exception:

        logger.exception(
            "Failed to read uploaded file "
            "username=%s",
            username,
        )

        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded image",
        )

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )

    # --------------------------------------------------------
    # Process image
    # --------------------------------------------------------

    try:

        result = face_detector.process_image(
            image_bytes=image_bytes,
            save_result=save_result,
        )

    except ValueError as exc:

        logger.warning(
            "Invalid image username=%s error=%s",
            username,
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:

        logger.exception(
            "Face detection failed username=%s",
            username,
        )

        raise HTTPException(
            status_code=500,
            detail="Face detection failed",
        )

    # --------------------------------------------------------
    # Add authenticated user information
    # --------------------------------------------------------

    result["user"] = username
    result["role"] = role

    logger.info(
        "Face detection completed "
        "username=%s faces=%s",
        username,
        result["num_faces"],
    )

    return result


# ============================================================
# SERVE DETECTED IMAGE
# ============================================================

@app.get(
    "/{token}/images/{filename}",
)
async def get_detected_image(
    token: str,
    filename: str,
):
    """
    Serve a detected image.

    IMPORTANT:
    The image is protected by JWT.

    URL:

        /<JWT>/images/<filename>
    """

    user = get_authenticated_user(
        token
    )

    safe_filename = validate_filename(
        filename
    )

    image_path = (
        DETECTED_DIR / safe_filename
    )

    if not image_path.exists():

        logger.warning(
            "Detected image not found "
            "username=%s filename=%s",
            user["username"],
            safe_filename,
        )

        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    logger.info(
        "Detected image accessed "
        "username=%s filename=%s",
        user["username"],
        safe_filename,
    )

    suffix = image_path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:

        media_type = "image/jpeg"

    elif suffix == ".webp":

        media_type = "image/webp"

    else:

        media_type = "image/png"

    response = FileResponse(
        image_path,
        media_type=media_type,
    )

    response.headers[
        "Cache-Control"
    ] = "no-store"

    response.headers[
        "Pragma"
    ] = "no-cache"

    return response


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,

        # VERY IMPORTANT:
        #
        # Do NOT allow Uvicorn's access logger to print:
        #
        #     GET /<JWT>/video
        #
        # Our middleware logs:
        #
        #     GET /<TOKEN>/video
        #
        access_log=False,

        log_level="info",
    )