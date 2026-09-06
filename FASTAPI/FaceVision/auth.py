from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import os

import jwt
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"

LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(BASE_DIR / ".env")


# ============================================================
# LOGGER
# ============================================================

auth_logger = logging.getLogger("auth")

if not auth_logger.handlers:
    auth_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        LOGS_DIR / "auth.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    auth_logger.addHandler(file_handler)

    auth_logger.propagate = False


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured in the .env file."
    )

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

try:
    TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "JWT_TOKEN_EXPIRE_MINUTES",
            "30",
        )
    )
except ValueError:
    raise RuntimeError(
        "JWT_TOKEN_EXPIRE_MINUTES must be a valid integer."
    )


# ============================================================
# USERS FROM .ENV
# ============================================================

def _get_env_user(prefix: str) -> tuple[str, dict]:
    """
    Load one user from environment variables.

    Expected variables:

        {prefix}_USERNAME
        {prefix}_PASSWORD
        {prefix}_ROLE
    """

    username = os.getenv(
        f"{prefix}_USERNAME"
    )

    password = os.getenv(
        f"{prefix}_PASSWORD"
    )

    role = os.getenv(
        f"{prefix}_ROLE"
    )

    if not username:
        raise RuntimeError(
            f"{prefix}_USERNAME is not configured."
        )

    if not password:
        raise RuntimeError(
            f"{prefix}_PASSWORD is not configured."
        )

    if not role:
        raise RuntimeError(
            f"{prefix}_ROLE is not configured."
        )

    return username, {
        "password": password,
        "role": role,
    }


admin_username, admin_user = _get_env_user(
    "AUTH_ADMIN"
)

normal_username, normal_user = _get_env_user(
    "AUTH_USER"
)


USERS = {
    admin_username: admin_user,
    normal_username: normal_user,
}


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# ============================================================
# CREATE JWT
# ============================================================

def create_access_token(
    username: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.
    """

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=TOKEN_EXPIRE_MINUTES
        )

    expire = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # NEVER log the JWT itself.
    auth_logger.info(
        "JWT created username=%s role=%s expires_at=%s",
        username,
        role,
        expire.isoformat(),
    )

    return token


# ============================================================
# VALIDATE JWT
# ============================================================

def validate_token(token: str) -> dict:
    """
    Validate JWT and return:

        {
            "username": "...",
            "role": "..."
        }
    """

    if not token:
        auth_logger.warning(
            "Authentication failed: empty token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username:
            auth_logger.warning(
                "Authentication failed: JWT missing subject"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        if not role:
            auth_logger.warning(
                "Authentication failed username=%s: missing role",
                username,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # Verify that the user still exists.
        user = USERS.get(username)

        if user is None:
            auth_logger.warning(
                "Authentication failed username=%s: user not found",
                username,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # Verify role against current configuration.
        if user["role"] != role:
            auth_logger.warning(
                "Authentication failed username=%s: role mismatch",
                username,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        auth_logger.info(
            "Authentication successful username=%s role=%s",
            username,
            role,
        )

        return {
            "username": username,
            "role": role,
        }

    except jwt.ExpiredSignatureError:

        auth_logger.warning(
            "Authentication failed: expired token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    except jwt.InvalidTokenError:

        auth_logger.warning(
            "Authentication failed: invalid token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict:

    return validate_token(token)


# ============================================================
# ADMIN CHECK
# ============================================================

def require_admin(
    user: dict = Depends(get_current_user),
) -> dict:

    if user.get("role") != "admin":

        auth_logger.warning(
            "Admin access denied username=%s",
            user.get(
                "username",
                "unknown",
            ),
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


# ============================================================
# GENERIC PERMISSION CHECK
# ============================================================

def require_permission(
    token: str,
    allowed_roles: list[str],
) -> dict:

    user = validate_token(token)

    username = user["username"]
    role = user["role"]

    if role not in allowed_roles:

        auth_logger.warning(
            "Permission denied username=%s role=%s allowed_roles=%s",
            username,
            role,
            allowed_roles,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return user