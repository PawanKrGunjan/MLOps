"""Locust load test for FaceVision FastAPI application.

Project:
    ~/Development/MLOps/FASTAPI

Test image:
    ./LOCAL/FACE_2026-09-06_06-30-25.jpg

Run:
    locust -f Testing/locustfile.py --host http://127.0.0.1:8000

Web UI:
    http://127.0.0.1:8089

Headless:
    locust \
        -f Testing/locustfile.py \
        --host http://127.0.0.1:8000 \
        --headless \
        -u 10 \
        -r 2 \
        -t 60s

JWT tokens are NEVER printed.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from locust import HttpUser, between, events, task

# ============================================================
# Load environment
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# Credentials
# ============================================================

ADMIN_USERNAME = os.getenv("AUTH_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("AUTH_ADMIN_PASSWORD")

USER_USERNAME = os.getenv("AUTH_USER_USERNAME")
USER_PASSWORD = os.getenv("AUTH_USER_PASSWORD")


# ============================================================
# Test image
# ============================================================

TEST_IMAGE = PROJECT_ROOT / "LOCAL" / "FACE_2026-09-06_06-30-25.jpg"


# ============================================================
# Logging
# ============================================================

logger = logging.getLogger("locust.facevision")


# ============================================================
# Counters
# ============================================================

LOGIN_SUCCESS = 0
LOGIN_FAILURE = 0
RATE_LIMIT_HITS = 0


# ============================================================
# Validate test image when Locust starts
# ============================================================

if not TEST_IMAGE.exists():
    raise FileNotFoundError(f"Test image not found:\n{TEST_IMAGE}")

if not TEST_IMAGE.is_file():
    raise FileNotFoundError(f"Test image is not a file:\n{TEST_IMAGE}")


# ============================================================
# Base Locust user
# ============================================================


class FaceVisionBaseUser(HttpUser):
    """Base class shared by normal and admin users."""

    abstract = True

    # Time between requests from the same simulated user.
    wait_time = between(0.5, 1.5)

    token = None
    username = None
    password = None
    role = None

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    def login(self):
        """Authenticate against POST /login.

        JWT is stored in memory only.
        JWT is NEVER printed.
        """
        global LOGIN_SUCCESS
        global LOGIN_FAILURE

        if not self.username or not self.password:
            logger.error("Authentication credentials are missing from .env")
            return False

        with self.client.post(
            "/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            name="POST /login",
            catch_response=True,
        ) as response:

            if response.status_code != 200:

                LOGIN_FAILURE += 1

                response.failure(f"Login failed: HTTP {response.status_code}")

                return False

            try:
                data = response.json()
            except ValueError:

                LOGIN_FAILURE += 1

                response.failure("Login returned invalid JSON")

                return False

            access_token = data.get("access_token")

            if not access_token:

                LOGIN_FAILURE += 1

                response.failure("Login response missing access_token")

                return False

            # Store token internally.
            # DO NOT print it.
            self.token = access_token

            LOGIN_SUCCESS += 1

            response.success()

            return True

    # --------------------------------------------------------
    # Start simulated user
    # --------------------------------------------------------

    def on_start(self):
        """Authenticate when a simulated user starts."""
        self.token = None

        self.login()

    # --------------------------------------------------------
    # Authentication headers
    # --------------------------------------------------------

    def auth_headers(self):
        """Return Bearer authentication headers."""
        if not self.token:
            return {}

        return {"Authorization": f"Bearer {self.token}"}

    # --------------------------------------------------------
    # Protected URL
    # --------------------------------------------------------

    def protected_path(self, suffix=""):
        """Build protected endpoint path.

        Examples:
            /<token>

            /<token>/video

            /<token>/detect-faces/

        The token is NEVER logged.

        """
        if not self.token:
            return None

        if suffix:
            return f"/{self.token}/{suffix.lstrip('/')}"

        return f"/{self.token}"

    # --------------------------------------------------------
    # Ensure authentication
    # --------------------------------------------------------

    def ensure_login(self):
        """Login again if this simulated user does not currently
        have a valid token.
        """
        if self.token:
            return True

        return self.login()


# ============================================================
# Normal User
# ============================================================


class FaceVisionUser(FaceVisionBaseUser):
    """Normal authenticated user.

    Credentials:
        AUTH_USER_USERNAME
        AUTH_USER_PASSWORD
    """

    # Approximately 90% normal users.
    weight = 9

    def on_start(self):

        self.username = USER_USERNAME
        self.password = USER_PASSWORD
        self.role = "user"

        super().on_start()

    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------

    @task(2)
    def health_check(self):

        with self.client.get(
            "/health",
            name="GET /health",
            catch_response=True,
        ) as response:

            if response.status_code != 200:

                response.failure(f"HTTP {response.status_code}")

            else:

                response.success()

    # --------------------------------------------------------
    # Detector status
    # --------------------------------------------------------

    @task(2)
    def detector_status(self):

        with self.client.get(
            "/detector-status",
            name="GET /detector-status",
            catch_response=True,
        ) as response:

            if response.status_code != 200:

                response.failure(f"HTTP {response.status_code}")

            else:

                response.success()

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    @task(4)
    def dashboard(self):

        if not self.ensure_login():
            return

        path = self.protected_path()

        with self.client.get(
            path,
            name="GET /<token>",
            catch_response=True,
        ) as response:

            if response.status_code == 200:

                response.success()

            elif response.status_code == 401:

                response.failure("Authentication failed")

                self.token = None

            elif response.status_code == 403:

                response.failure("Permission denied")

            elif response.status_code == 429:

                response.failure("Rate limited (429)")

            else:

                response.failure(f"HTTP {response.status_code}")

    # --------------------------------------------------------
    # Video
    # --------------------------------------------------------

    @task(1)
    def video_stream(self):

        if not self.ensure_login():
            return

        path = self.protected_path("video")

        with self.client.get(
            path,
            name="GET /<token>/video",
            stream=True,
            catch_response=True,
        ) as response:

            if response.status_code == 200:

                response.success()

            elif response.status_code == 401:

                response.failure("Authentication failed")

                self.token = None

            elif response.status_code == 403:

                response.failure("Permission denied")

            elif response.status_code == 429:

                response.failure("Rate limited (429)")

            else:

                response.failure(f"HTTP {response.status_code}")

    # --------------------------------------------------------
    # Face Detection
    # --------------------------------------------------------

    @task(6)
    def detect_faces(self):

        if not self.ensure_login():
            return

        path = self.protected_path("detect-faces/")

        # IMPORTANT:
        # Open the real image for every request.
        #
        # This makes the Locust test use:
        #
        # ./LOCAL/FACE_2026-09-06_06-30-25.jpg
        #
        # instead of a generated dummy image.
        try:

            with TEST_IMAGE.open("rb") as image_file:

                files = {
                    "file": (
                        TEST_IMAGE.name,
                        image_file,
                        "image/jpeg",
                    ),
                }

                with self.client.post(
                    path,
                    files=files,
                    headers=self.auth_headers(),
                    name="POST /<token>/detect-faces/",
                    catch_response=True,
                ) as response:

                    if response.status_code == 200:

                        response.success()

                    elif response.status_code == 401:

                        response.failure("Authentication failed")

                        self.token = None

                    elif response.status_code == 403:

                        response.failure("Permission denied")

                    elif response.status_code == 429:

                        response.failure("Rate limited (429)")

                    else:

                        response.failure(f"HTTP {response.status_code}")

        except OSError as exc:

            logger.error(
                "Unable to read test image: %s",
                exc,
            )

    # --------------------------------------------------------
    # Rate-limit test
    # --------------------------------------------------------

    @task(1)
    def rate_limit_test(self):

        global RATE_LIMIT_HITS

        if not self.ensure_login():
            return

        path = self.protected_path()

        with self.client.get(
            path,
            name="RATE LIMIT /<token>",
            catch_response=True,
        ) as response:

            if response.status_code == 429:

                RATE_LIMIT_HITS += 1

                # 429 is expected for this particular
                # rate-limit observation request.
                response.success()

            elif response.status_code == 200:

                response.success()

            elif response.status_code == 401:

                response.failure("Authentication failed")

                self.token = None

            else:

                response.failure(f"Unexpected HTTP {response.status_code}")


# ============================================================
# Admin User
# ============================================================


class FaceVisionAdminUser(FaceVisionBaseUser):
    """Admin authenticated user.

    Credentials:
        AUTH_ADMIN_USERNAME
        AUTH_ADMIN_PASSWORD
    """

    # Approximately 10% admin users.
    weight = 1

    def on_start(self):

        self.username = ADMIN_USERNAME
        self.password = ADMIN_PASSWORD
        self.role = "admin"

        super().on_start()

    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------

    @task(2)
    def health_check(self):

        with self.client.get(
            "/health",
            name="GET /health [ADMIN]",
            catch_response=True,
        ) as response:

            if response.status_code != 200:

                response.failure(f"HTTP {response.status_code}")

            else:

                response.success()

    # --------------------------------------------------------
    # Detector status
    # --------------------------------------------------------

    @task(2)
    def detector_status(self):

        with self.client.get(
            "/detector-status",
            name="GET /detector-status [ADMIN]",
            catch_response=True,
        ) as response:

            if response.status_code != 200:

                response.failure(f"HTTP {response.status_code}")

            else:

                response.success()

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    @task(4)
    def dashboard(self):

        if not self.ensure_login():
            return

        path = self.protected_path()

        with self.client.get(
            path,
            name="GET /<token> [ADMIN]",
            catch_response=True,
        ) as response:

            if response.status_code == 200:

                response.success()

            elif response.status_code == 401:

                response.failure("Authentication failed")

                self.token = None

            elif response.status_code == 403:

                response.failure("Permission denied")

            elif response.status_code == 429:

                response.failure("Rate limited (429)")

            else:

                response.failure(f"HTTP {response.status_code}")

    # --------------------------------------------------------
    # Face Detection
    # --------------------------------------------------------

    @task(6)
    def detect_faces(self):

        if not self.ensure_login():
            return

        path = self.protected_path("detect-faces/")

        try:

            with TEST_IMAGE.open("rb") as image_file:

                files = {
                    "file": (
                        TEST_IMAGE.name,
                        image_file,
                        "image/jpeg",
                    ),
                }

                with self.client.post(
                    path,
                    files=files,
                    headers=self.auth_headers(),
                    name="POST /<token>/detect-faces/ [ADMIN]",
                    catch_response=True,
                ) as response:

                    if response.status_code == 200:

                        response.success()

                    elif response.status_code == 401:

                        response.failure("Authentication failed")

                        self.token = None

                    elif response.status_code == 403:

                        response.failure("Permission denied")

                    elif response.status_code == 429:

                        response.failure("Rate limited (429)")

                    else:

                        response.failure(f"HTTP {response.status_code}")

        except OSError as exc:

            logger.error(
                "Unable to read test image: %s",
                exc,
            )

    # --------------------------------------------------------
    # Rate Limit
    # --------------------------------------------------------

    @task(1)
    def rate_limit_test(self):

        global RATE_LIMIT_HITS

        if not self.ensure_login():
            return

        path = self.protected_path()

        with self.client.get(
            path,
            name="RATE LIMIT /<token> [ADMIN]",
            catch_response=True,
        ) as response:

            if response.status_code == 429:

                RATE_LIMIT_HITS += 1

                response.success()

            elif response.status_code == 200:

                response.success()

            elif response.status_code == 401:

                response.failure("Authentication failed")

                self.token = None

            else:

                response.failure(f"Unexpected HTTP {response.status_code}")


# ============================================================
# Test Start
# ============================================================


@events.test_start.add_listener
def on_test_start(environment, **kwargs):

    logger.info("=" * 70)
    logger.info("FaceVision Locust Load Test Started")
    logger.info("=" * 70)

    logger.info(
        "Target: %s",
        environment.host,
    )

    logger.info(
        "Test image: %s",
        TEST_IMAGE,
    )

    logger.info(
        "Test image size: %d bytes",
        TEST_IMAGE.stat().st_size,
    )

    logger.info(
        "Normal user configured: %s",
        bool(USER_USERNAME and USER_PASSWORD),
    )

    logger.info(
        "Admin user configured: %s",
        bool(ADMIN_USERNAME and ADMIN_PASSWORD),
    )

    logger.info("JWT tokens will NOT be logged.")

    logger.info("=" * 70)


# ============================================================
# Test Stop
# ============================================================


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):

    logger.info("=" * 70)
    logger.info("FaceVision Locust Load Test Finished")
    logger.info("=" * 70)

    logger.info(
        "Login successes: %d",
        LOGIN_SUCCESS,
    )

    logger.info(
        "Login failures: %d",
        LOGIN_FAILURE,
    )

    logger.info(
        "HTTP 429 responses observed: %d",
        RATE_LIMIT_HITS,
    )

    logger.info("=" * 70)
