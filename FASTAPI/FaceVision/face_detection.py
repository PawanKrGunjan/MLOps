from __future__ import annotations

import logging
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOCAL_DIR = BASE_DIR / "LOCAL"

# Directory where detected images are stored
DETECTED_DIR = LOCAL_DIR / "detected"

DETECTED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOGGER
# ============================================================

LOGS_DIR = BASE_DIR / "logs"

LOGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

logger = logging.getLogger("face_detection")

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    file_handler = logging.FileHandler(
        LOGS_DIR / "face_detection.log",
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Prevent duplicate logs
    logger.propagate = False


# ============================================================
# HAAR CASCADE
# ============================================================

ROOT_FACE_CASCADE_PATH = Path(
    "/harr_casscade_classifiers/haarcascade_frontalface_default.xml"
)
ROOT_EYE_CASCADE_PATH = Path("/harr_casscade_classifiers/haarcascade_eye.xml")

PROJECT_FACE_CASCADE_PATH = (
    BASE_DIR / "harr_casscade_classifiers" / "haarcascade_frontalface_default.xml"
)
PROJECT_EYE_CASCADE_PATH = (
    BASE_DIR / "harr_casscade_classifiers" / "haarcascade_eye.xml"
)

FACE_CASCADE_PATH = (
    ROOT_FACE_CASCADE_PATH
    if ROOT_FACE_CASCADE_PATH.exists()
    else PROJECT_FACE_CASCADE_PATH
)
EYE_CASCADE_PATH = (
    ROOT_EYE_CASCADE_PATH
    if ROOT_EYE_CASCADE_PATH.exists()
    else PROJECT_EYE_CASCADE_PATH
)

CASCADE_PATH = FACE_CASCADE_PATH


# ============================================================
# FACE DETECTOR
# ============================================================


class FaceDetector:
    """OpenCV face detector.

    Responsibilities:
        - Load Haar Cascade
        - Detect faces
        - Draw bounding boxes
        - Process uploaded images
        - Save detected images
        - Process webcam frames
    """

    def __init__(
        self,
        cascade_path: Path | str | None = None,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: tuple[int, int] = (30, 30),
    ) -> None:

        self.cascade_path = Path(cascade_path or CASCADE_PATH)

        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

        self.face_cascade = None
        self.eye_cascade = None

        self._load_cascade()

    # ========================================================
    # LOAD CASCADE
    # ========================================================

    def _load_cascade(self) -> None:
        """Load OpenCV Haar Cascade files."""
        if not self.cascade_path.exists():

            logger.error(
                "Haar Cascade not found: %s",
                self.cascade_path,
            )

            raise FileNotFoundError(f"Haar Cascade not found: {self.cascade_path}")

        self.face_cascade = cv2.CascadeClassifier(str(self.cascade_path))
        self.eye_cascade = cv2.CascadeClassifier(str(EYE_CASCADE_PATH))

        if self.face_cascade.empty() or self.eye_cascade.empty():

            logger.error(
                "Failed to load Haar Cascade: face=%s eye=%s",
                self.cascade_path,
                EYE_CASCADE_PATH,
            )

            raise RuntimeError("Failed to load OpenCV Haar Cascade")

        logger.info("Face detector initialized successfully")

    # ========================================================
    # DETECT FACES
    # ========================================================

    def detect_faces(
        self,
        image: np.ndarray,
    ) -> list[dict[str, int]]:
        """Detect faces in an OpenCV image.

        Returns:
        [
            {
                "x": 100,
                "y": 50,
                "w": 150,
                "h": 150
            }
        ]

        """
        if image is None:

            raise ValueError("Image cannot be None")

        if not isinstance(image, np.ndarray):

            raise TypeError("Image must be a NumPy array")

        if image.size == 0:

            raise ValueError("Image is empty")

        # Convert BGR image to grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        detected_faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
        )

        faces = []

        for x, y, w, h in detected_faces:

            faces.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h),
                },
            )

        logger.info(
            "Face detection completed faces=%d",
            len(faces),
        )

        return faces

    # ========================================================
    # DRAW FACE BOXES
    # ========================================================

    def draw_faces(
        self,
        image: np.ndarray,
        faces: list[dict[str, int]],
    ) -> np.ndarray:
        """Draw bounding boxes around detected faces."""
        output = image.copy()

        for index, face in enumerate(faces, start=1):

            x = face["x"]
            y = face["y"]
            w = face["w"]
            h = face["h"]

            # Bounding box
            cv2.rectangle(
                output,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2,
            )

            # Face label
            label = f"Face {index}"

            cv2.putText(
                output,
                label,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        return output

    # ========================================================
    # DETECT + DRAW
    # ========================================================

    def detect_and_draw(
        self,
        image: np.ndarray,
    ) -> tuple[np.ndarray, list[dict[str, int]]]:
        """Detect faces and draw bounding boxes.

        Returns:
            output_image
            faces

        """
        faces = self.detect_faces(image)

        output = self.draw_faces(
            image,
            faces,
        )

        return output, faces

    # ========================================================
    # READ IMAGE
    # ========================================================

    def read_image(
        self,
        image_path: Path | str,
    ) -> np.ndarray:
        """Read an image from disk."""
        image_path = Path(image_path)

        if not image_path.exists():

            logger.error(
                "Image not found: %s",
                image_path,
            )

            raise FileNotFoundError(f"Image not found: {image_path}")

        image = cv2.imread(str(image_path))

        if image is None:

            logger.error(
                "Unable to read image: %s",
                image_path,
            )

            raise ValueError(f"Unable to read image: {image_path}")

        return image

    # ========================================================
    # DECODE IMAGE BYTES
    # ========================================================

    def decode_image(
        self,
        image_bytes: bytes,
    ) -> np.ndarray:
        """Convert uploaded image bytes into an OpenCV image."""
        if not image_bytes:

            raise ValueError("Uploaded image is empty")

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:

            logger.warning("Unable to decode uploaded image")

            raise ValueError("Invalid or unsupported image")

        return image

    # ========================================================
    # SAVE IMAGE
    # ========================================================

    def save_image(
        self,
        image: np.ndarray,
        filename: str | None = None,
    ) -> Path:
        """Save an OpenCV image to LOCAL/detected.

        Returns:
            Path of saved image.

        """
        if image is None:

            raise ValueError("Cannot save empty image")

        if filename is None:

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

            filename = f"FACE_{timestamp}.jpg"

        # Prevent directory traversal
        filename = Path(filename).name

        output_path = DETECTED_DIR / filename

        success = cv2.imwrite(
            str(output_path),
            image,
        )

        if not success:

            logger.error(
                "Failed to save image: %s",
                output_path,
            )

            raise OSError(f"Failed to save image: {output_path}")

        logger.info(
            "Detected image saved: %s",
            output_path.name,
        )

        return output_path

    # ========================================================
    # PROCESS UPLOADED IMAGE
    # ========================================================

    def process_image(
        self,
        image_bytes: bytes,
        save_result: bool = True,
        filename: str | None = None,
    ) -> dict:
        """Complete uploaded-image processing pipeline.

        Steps:

            image bytes
                 ↓
            decode image
                 ↓
            detect faces
                 ↓
            draw bounding boxes
                 ↓
            optionally save
                 ↓
            return result
        """
        logger.info("Processing uploaded image")

        image = self.decode_image(image_bytes)

        output_image, faces = self.detect_and_draw(image)

        image_path = None

        if save_result:

            image_path = self.save_image(
                output_image,
                filename=filename,
            )

        result = {
            "image_path": (
                str(image_path.relative_to(BASE_DIR)) if image_path else None
            ),
            "num_faces": len(faces),
            "faces": faces,
        }

        logger.info(
            "Image processing completed faces=%d saved=%s",
            len(faces),
            save_result,
        )

        return result

    # ========================================================
    # WEBCAM FRAME PROCESSING
    # ========================================================

    def process_frame(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """Detect faces in a webcam frame and return
        the frame with bounding boxes.
        """
        if frame is None:

            return frame

        output, _ = self.detect_and_draw(frame)

        return output


# ============================================================
# GLOBAL DETECTOR INSTANCE
# ============================================================

face_detector = FaceDetector()


# ============================================================
# WEBCAM
# ============================================================


def generate_frames(
    camera_index: int = 0,
) -> Generator[bytes, None, None]:
    """Generate webcam frames for FastAPI StreamingResponse.

    Output format:

        multipart/x-mixed-replace
    """
    logger.info(
        "Starting camera index=%d",
        camera_index,
    )

    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():

        logger.error(
            "Unable to open camera index=%d",
            camera_index,
        )

        raise RuntimeError(f"Unable to open camera {camera_index}")

    try:

        while True:

            success, frame = camera.read()

            if not success:

                logger.warning("Failed to read camera frame")

                break

            # Face detection
            frame = face_detector.process_frame(frame)

            # Encode frame as JPEG
            success, buffer = cv2.imencode(
                ".jpg",
                frame,
            )

            if not success:

                logger.warning("Failed to encode camera frame")

                continue

            frame_bytes = buffer.tobytes()

            # FastAPI streaming format
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"\r\n" + frame_bytes + b"\r\n"
            )

    except GeneratorExit:

        logger.info("Camera stream closed by client")

    except Exception:

        logger.exception("Unexpected error during camera streaming")

    finally:

        camera.release()

        logger.info(
            "Camera released index=%d",
            camera_index,
        )


# ============================================================
# SINGLE FRAME CAPTURE
# ============================================================


def capture_frame(
    camera_index: int = 0,
) -> np.ndarray:
    """Capture one frame from the camera.

    Useful for testing.
    """
    logger.info(
        "Capturing single frame camera=%d",
        camera_index,
    )

    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():

        logger.error(
            "Unable to open camera=%d",
            camera_index,
        )

        raise RuntimeError(f"Unable to open camera {camera_index}")

    try:

        success, frame = camera.read()

        if not success:

            raise RuntimeError("Unable to capture camera frame")

        return frame

    finally:

        camera.release()


# ============================================================
# CAPTURE + DETECT
# ============================================================


def capture_and_detect(
    camera_index: int = 0,
    save_result: bool = True,
) -> dict:
    """Capture one webcam frame, detect faces and optionally
    save the resulting image.
    """
    frame = capture_frame(camera_index)

    output, faces = face_detector.detect_and_draw(frame)

    image_path = None

    if save_result:

        image_path = face_detector.save_image(output)

    return {
        "image_path": (str(image_path.relative_to(BASE_DIR)) if image_path else None),
        "num_faces": len(faces),
        "faces": faces,
    }


# ============================================================
# SIMPLE HEALTH CHECK
# ============================================================


def detector_status() -> dict:
    """Return detector status.

    Useful for /health or debugging.
    """
    return {
        "detector": "opencv_haar_cascade",
        "cascade_exists": CASCADE_PATH.exists(),
        "cascade_path": str(CASCADE_PATH),
        "output_directory": str(DETECTED_DIR),
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("Face Detection Module")

    print(detector_status())
