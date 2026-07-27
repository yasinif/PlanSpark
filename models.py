"""
models.py — SQLAlchemy models for the Persian To-Do List app.

Models:
    User            — registered user with hashed password
    Task            — task belonging to a user (status computed, never stored)
    CustomPriority  — user-defined priority label (max 5 per user)

Rules:
    - All DateTime fields are naive UTC (no tzinfo). Never store aware datetimes.
    - @validates decorators raise ValueError (not silently truncate) on invalid data.
    - Cascade deletes: removing a User removes all their Tasks and CustomPriorities.
    - Composite index on (is_done, expires_at) for efficient status queries.
"""

# =====================================================================
# FILE: models.py
# PURPOSE: Defines SQLAlchemy ORM models for User, Task, and CustomPriority with validation decorators, relationships, and composite indexes.
# =====================================================================

import re
from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from sqlalchemy.orm import validates

db = SQLAlchemy()

# ---------------------------------------------------------------------
# VALIDATION CONSTANTS: Regex patterns and allowed value sets
# ---------------------------------------------------------------------
# Name fields: accept Persian script, Latin letters (A-Z/a-z), and spaces.
# Explicitly rejects: ASCII digits (0-9), Persian digits (۰-۹), symbols, punctuation.
NAME_REGEX = re.compile(
    r"^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200c A-Za-z]+$"
)
# Username: strict ASCII alphanumeric only.
# Explicitly rejects: Persian/Unicode letters, underscores, spaces, symbols.
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

VALID_LANGUAGES = {"fa", "en"}
VALID_DATE_FORMATS = {"jalali", "gregorian"}
VALID_DATE_STYLES = {"text", "numeric"}


# ---------------------------------------------------------------------
# USER MODEL: Registered user with hashed credentials and preferences
# ---------------------------------------------------------------------

class User(UserMixin, db.Model):
    """Registered user. Passwords are stored as bcrypt hashes only."""

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name: str = db.Column(db.String(30), nullable=False)
    family: str = db.Column(db.String(30), nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)
    # Delta 2.4: language and date_format preferences
    language: str = db.Column(db.String(2), nullable=False, default="fa")
    date_format: str = db.Column(db.String(10), nullable=False, default="jalali")
    date_display_style: str = db.Column(db.String(10), nullable=False, default="text")
    # ---  Recovery System Fields ---
    recovery_w1_hash: str = db.Column(db.String(128), nullable=False)
    recovery_w2_hash: str = db.Column(db.String(128), nullable=False)
    
    # ---  Rate Limiting Fields ---
    recovery_attempts: int = db.Column(db.Integer, nullable=False, default=0)
    last_recovery_attempt: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    # Relationships with cascading deletes
    tasks = db.relationship(
        "Task",
        backref="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    custom_priorities = db.relationship(
        "CustomPriority",
        backref="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"

    # ---  Field Validators ---

    @validates("username")
    def validate_username(self, key: str, value: str) -> str:
        """Enforce username length (5–20) and alphanumeric/underscore pattern."""
        value = value.strip()
        if not (5 <= len(value) <= 20):
            raise ValueError("val_username_length")
        if not USERNAME_REGEX.match(value):
            raise ValueError("val_username_format")
        return value

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Enforce name length (2–30) and bilingual (Persian/Latin) letter-only character set."""
        value = value.strip()
        if not (2 <= len(value) <= 30):
            raise ValueError("val_name_length")
        if not NAME_REGEX.match(value):
            raise ValueError("val_name_letters_only")
        return value

    @validates("family")
    def validate_family(self, key: str, value: str) -> str:
        """Enforce family name length (2–30) and bilingual (Persian/Latin) letter-only character set."""
        value = value.strip()
        if not (2 <= len(value) <= 30):
            raise ValueError("val_family_length")
        if not NAME_REGEX.match(value):
            raise ValueError("val_family_letters_only")
        return value

    @validates("language")
    def validate_language(self, key: str, value: str) -> str:
        """Enforce language is 'fa' or 'en'."""
        value = value.strip().lower()
        if value not in VALID_LANGUAGES:
            raise ValueError(f"زبان باید یکی از {VALID_LANGUAGES} باشد.")
        return value

    @validates("date_format")
    def validate_date_format(self, key: str, value: str) -> str:
        """Enforce date_format is 'jalali' or 'gregorian'."""
        value = value.strip().lower()
        if value not in VALID_DATE_FORMATS:
            raise ValueError(f"فرمت تاریخ باید یکی از {VALID_DATE_FORMATS} باشد.")
        return value

    @validates("date_display_style")
    def validate_date_display_style(self, key: str, value: str) -> str:
        """Enforce date_display_style is 'text' or 'numeric'."""
        value = value.strip().lower()
        if value not in VALID_DATE_STYLES:
            raise ValueError(f"استایل تاریخ باید یکی از {VALID_DATE_STYLES} باشد.")
        return value


# ---------------------------------------------------------------------
# TASK MODEL: User task with computed status and Jalali deadline
# ---------------------------------------------------------------------

class Task(db.Model):
    """
    A task owned by a user.

    Status is computed at query time — never stored:
        pending  → is_done=False AND expires_at >= NOW()
        done     → is_done=True
        expired  → is_done=False AND expires_at < NOW()
    """

    __tablename__ = "tasks"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: str = db.Column(db.String(100), nullable=False)
    description: Optional[str] = db.Column(db.String(500), nullable=True)
    priority: Optional[str] = db.Column(db.String(50), nullable=True, index=True)
    expires_at: datetime = db.Column(db.DateTime, nullable=False, index=True)
    estimated_time: Optional[int] = db.Column(db.Integer, nullable=True)  # minutes
    is_done: bool = db.Column(db.Boolean, nullable=False, default=False)
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} is_done={self.is_done}>"

    # ---  Field Validators ---

    @validates("title")
    def validate_title(self, key: str, value: str) -> str:
        """Enforce title is present and max 100 characters."""
        value = value.strip()
        if not value:
            raise ValueError("val_title_required")
        if len(value) > 100:
            raise ValueError("val_title_length")
        return value

    @validates("description")
    def validate_description(self, key: str, value: Optional[str]) -> Optional[str]:
        """Enforce description max 500 characters."""
        if value is None:
            return value
        value = value.strip()
        if len(value) > 500:
            raise ValueError("val_description_length")
        return value or None

    @validates("estimated_time")
    def validate_estimated_time(self, key: str, value: Optional[int]) -> Optional[int]:
        """Enforce estimated_time is non-negative if provided."""
        if value is None:
            return value
        if value < 0:
            raise ValueError("val_estimated_negative")
        return value


# ---------------------------------------------------------------------
# CUSTOM PRIORITY MODEL: User-defined priority labels
# ---------------------------------------------------------------------

class CustomPriority(db.Model):
    """
    A user-defined priority label.
    Max 5 per user (enforced at application level, not DB level).
    """

    __tablename__ = "custom_priorities"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: str = db.Column(db.String(15), nullable=False)

    def __repr__(self) -> str:
        return f"<CustomPriority id={self.id} name={self.name!r} user_id={self.user_id}>"

    # ---  Field Validators ---

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Enforce priority name length (2–15) and non-empty."""
        value = value.strip()
        if not (2 <= len(value) <= 15):
            raise ValueError("val_priority_name_length")
        return value


# ---------------------------------------------------------------------
# DATABASE INDEXES: Composite index for efficient status queries
# ---------------------------------------------------------------------

# Composite index for efficient status filtering (is_done + expires_at)
Index("ix_tasks_is_done_expires", Task.is_done, Task.expires_at)
