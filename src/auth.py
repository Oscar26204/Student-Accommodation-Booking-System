"""Registration and login for students and landlords (backlog items 1 and 2)."""
from __future__ import annotations

import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from enum import Enum

from .errors import AuthenticationError, DuplicateUserError, ValidationError
from .storage import Repository

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class Role(str, Enum):
    STUDENT = "student"
    LANDLORD = "landlord"


@dataclass(frozen=True)
class User:
    user_id: int
    full_name: str
    email: str
    role: Role
    password_hash: str
    phone: str = ""


def hash_password(password: str) -> str:
    """Return 'scrypt$<salt>$<hash>'. Passwords are never stored in plain text."""
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    candidate = hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1
    )
    return hmac.compare_digest(candidate.hex(), digest_hex)


def validate_email(email: str) -> str:
    cleaned = (email or "").strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        raise ValidationError("Enter a valid email address.")
    return cleaned


def validate_password(password: str) -> None:
    if (
        not password
        or len(password) < MIN_PASSWORD_LENGTH
        or not any(c.isalpha() for c in password)
        or not any(c.isdigit() for c in password)
    ):
        raise ValidationError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters "
            "and contain a letter and a digit."
        )


def validate_phone(phone: str) -> str:
    digits = re.sub(r"[\s\-]", "", phone or "")
    if not re.fullmatch(r"(\+254|0)\d{9}", digits):
        raise ValidationError("Enter a valid Kenyan phone number, e.g. 0712345678.")
    return digits


class AuthService:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    # -- registration ---------------------------------------------------
    def register_student(self, full_name: str, email: str, password: str) -> User:
        return self._register(Role.STUDENT, full_name, email, password, phone="")

    def register_landlord(
        self, full_name: str, email: str, password: str, phone: str
    ) -> User:
        return self._register(
            Role.LANDLORD, full_name, email, password, phone=validate_phone(phone)
        )

    def _register(
        self, role: Role, full_name: str, email: str, password: str, phone: str
    ) -> User:
        if not (full_name or "").strip():
            raise ValidationError("Full name is required.")
        email = validate_email(email)
        validate_password(password)
        if self._find_by_email(email) is not None:
            raise DuplicateUserError("An account with this email already exists.")
        user = User(
            user_id=self._repo.next_user_id(),
            full_name=full_name.strip(),
            email=email,
            role=role,
            password_hash=hash_password(password),
            phone=phone,
        )
        self._repo.users[user.user_id] = user
        return user

    # -- login ----------------------------------------------------------
    def login(self, email: str, password: str) -> User:
        # One generic message so attackers cannot learn which emails exist.
        user = self._find_by_email((email or "").strip().lower())
        if user is None or not verify_password(password or "", user.password_hash):
            raise AuthenticationError("Incorrect email or password.")
        return user

    def _find_by_email(self, email: str) -> User | None:
        for user in self._repo.users.values():
            if user.email == email:
                return user
        return None
