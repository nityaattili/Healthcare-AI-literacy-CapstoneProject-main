from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import APP_SQLITE_PATH, DATA_DIR

VALID_ROLES = ("admin", "instructor", "student")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,64}$")


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        str(APP_SQLITE_PATH),
        check_same_thread=False,
        timeout=30.0,
    )
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390_000)
    return salt.hex(), dk.hex()


def _verify_password(password: str, salt_hex: str, stored_hash_hex: str) -> bool:
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(stored_hash_hex)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390_000)
    return hmac.compare_digest(dk, expected)


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def _migrate_legacy_users(conn: sqlite3.Connection) -> None:
    if not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone():
        return
    cols = _table_columns(conn, "users")
    if "is_active" in cols and "role" in cols:
        return
    conn.executescript(
        """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            display_name TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login_at TEXT
        );
        INSERT INTO users_new (id, username, password_salt, password_hash, role, display_name, is_active, created_at, last_login_at)
        SELECT id, username, password_salt, password_hash, role, display_name, 1, created_at, last_login_at FROM users;
        DROP TABLE users;
        ALTER TABLE users_new RENAME TO users;
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """
    )


def _ensure_supervised_by_column(conn: sqlite3.Connection) -> None:
    if not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone():
        return
    cols = _table_columns(conn, "users")
    if "supervised_by" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN supervised_by INTEGER")


def init_app_database() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                display_name TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login_at TEXT,
                supervised_by INTEGER
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.commit()
        _migrate_legacy_users(conn)
        conn.commit()
        _ensure_supervised_by_column(conn)
        conn.commit()
        seed_standard_accounts_if_enabled()
        conn.commit()
    finally:
        conn.close()


def seed_standard_accounts_if_enabled() -> None:
    if os.getenv("AIL_SEED_STANDARD_ACCOUNTS", "").strip().lower() not in ("1", "true", "yes", "on"):
        return
    if user_count() > 0:
        return
    now = datetime.now(timezone.utc).isoformat()
    triples = [
        (
            "admin",
            os.getenv("AIL_SEED_ADMIN_PASSWORD", "Admin@Healthcare2026!"),
            "admin",
            "Administrator",
        ),
        (
            "instructor",
            os.getenv("AIL_SEED_INSTRUCTOR_PASSWORD", "Instructor@Healthcare2026!"),
            "instructor",
            "Instructor",
        ),
        (
            "student",
            os.getenv("AIL_SEED_STUDENT_PASSWORD", "Student@Healthcare2026!"),
            "student",
            "Student",
        ),
    ]
    conn = _connect()
    try:
        for uname, pw, role, dname in triples:
            u = uname.strip().lower()
            if not _USERNAME_RE.match(u) or len(pw) < 8:
                continue
            salt, ph = _hash_password(pw)
            conn.execute(
                """
                INSERT INTO users (username, password_salt, password_hash, role, display_name, is_active, created_at, supervised_by)
                VALUES (?, ?, ?, ?, ?, 1, ?, NULL)
                """,
                (u, salt, ph, role, dname, now),
            )
        conn.commit()
    finally:
        conn.close()


def user_count() -> int:
    conn = _connect()
    try:
        return int(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0])
    finally:
        conn.close()


def create_bootstrap_admin(username: str, password: str, display_name: str) -> Tuple[bool, str]:
    if user_count() > 0:
        return False, "System is already initialized."
    u = username.strip().lower()
    if not _USERNAME_RE.match(u):
        return False, "Username: 3–64 chars, letters, digits, . _ -"
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    dn = (display_name or u).strip() or u
    salt, ph = _hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO users (username, password_salt, password_hash, role, display_name, is_active, created_at, supervised_by)
            VALUES (?, ?, ?, 'admin', ?, 1, ?, NULL)
            """,
            (u, salt, ph, dn, now),
        )
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    finally:
        conn.close()


def register_pending_account(username: str, password: str, display_name: str) -> Tuple[bool, str]:
    u = username.strip().lower()
    if not _USERNAME_RE.match(u):
        return False, "Username: 3–64 chars, letters, digits, . _ -"
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    dn = (display_name or u).strip() or u
    salt, ph = _hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO users (username, password_salt, password_hash, role, display_name, is_active, created_at, supervised_by)
            VALUES (?, ?, ?, 'student', ?, 0, ?, NULL)
            """,
            (u, salt, ph, dn, now),
        )
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "That username is already registered."
    finally:
        conn.close()


def verify_credentials(username: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not username or not password:
        return None, "invalid"
    uname = username.strip().lower()
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT id, username, password_salt, password_hash, role, display_name, is_active
            FROM users WHERE username = ?
            """,
            (uname,),
        ).fetchone()
        if row is None:
            return None, "invalid"
        if not int(row["is_active"]):
            return None, "inactive"
        if not _verify_password(password, row["password_salt"], row["password_hash"]):
            return None, "invalid"
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), row["id"]),
        )
        conn.commit()
        return (
            {
                "id": int(row["id"]),
                "username": row["username"],
                "role": row["role"],
                "display_name": row["display_name"] or row["username"],
                "is_active": bool(int(row["is_active"])),
            },
            None,
        )
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT id, username, role, display_name, is_active FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": int(row["id"]),
            "username": row["username"],
            "role": row["role"],
            "display_name": row["display_name"] or row["username"],
            "is_active": bool(int(row["is_active"])),
        }
    finally:
        conn.close()


def list_users_admin() -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        cols = _table_columns(conn, "users")
        if "supervised_by" in cols:
            rows = conn.execute(
                """
                SELECT u.id, u.username, u.role, u.display_name, u.is_active, u.created_at, u.last_login_at,
                       u.supervised_by, sup.username AS supervisor_username
                FROM users u
                LEFT JOIN users sup ON sup.id = u.supervised_by
                ORDER BY u.id
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, username, role, display_name, is_active, created_at, last_login_at
                FROM users ORDER BY id
                """
            ).fetchall()
        out = []
        for r in rows:
            d = {
                "id": int(r["id"]),
                "username": r["username"],
                "role": r["role"],
                "display_name": r["display_name"] or r["username"],
                "is_active": bool(int(r["is_active"])),
                "created_at": r["created_at"],
                "last_login_at": r["last_login_at"],
            }
            if "supervised_by" in cols:
                d["supervised_by"] = r["supervised_by"]
                d["supervisor_username"] = r["supervisor_username"]
            else:
                d["supervised_by"] = None
                d["supervisor_username"] = None
            out.append(d)
        return out
    finally:
        conn.close()


def list_instructors_for_select() -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT id, username, display_name FROM users
            WHERE role = 'instructor' AND is_active = 1
            ORDER BY username
            """
        ).fetchall()
        return [
            {"id": int(r["id"]), "username": r["username"], "display_name": r["display_name"] or r["username"]}
            for r in rows
        ]
    finally:
        conn.close()


def list_students_for_instructor_dashboard(instructor_id: int) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        cols = _table_columns(conn, "users")
        if "supervised_by" not in cols:
            rows = conn.execute(
                """
                SELECT id, username, display_name, is_active, last_login_at, created_at
                FROM users WHERE role = 'student' ORDER BY username
                """
            ).fetchall()
            return [
                {
                    "id": int(r["id"]),
                    "username": r["username"],
                    "display_name": r["display_name"] or r["username"],
                    "is_active": bool(int(r["is_active"])),
                    "last_login_at": r["last_login_at"],
                    "created_at": r["created_at"],
                    "supervisor_username": "—",
                    "assigned_to_me": False,
                }
                for r in rows
            ]
        rows = conn.execute(
            """
            SELECT u.id, u.username, u.display_name, u.is_active, u.last_login_at, u.created_at,
                   u.supervised_by, sup.username AS supervisor_username,
                   CASE WHEN u.supervised_by = ? THEN 1 ELSE 0 END AS assigned_to_me
            FROM users u
            LEFT JOIN users sup ON sup.id = u.supervised_by
            WHERE u.role = 'student'
              AND (u.supervised_by IS NULL OR u.supervised_by = ?)
            ORDER BY assigned_to_me DESC, u.username
            """,
            (instructor_id, instructor_id),
        ).fetchall()
        return [
            {
                "id": int(r["id"]),
                "username": r["username"],
                "display_name": r["display_name"] or r["username"],
                "is_active": bool(int(r["is_active"])),
                "last_login_at": r["last_login_at"],
                "created_at": r["created_at"],
                "supervisor_username": r["supervisor_username"] or "—",
                "assigned_to_me": bool(int(r["assigned_to_me"])),
            }
            for r in rows
        ]
    finally:
        conn.close()


def count_active_admins_except(conn: sqlite3.Connection, exclude_id: Optional[int]) -> int:
    if exclude_id is None:
        return int(
            conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1"
            ).fetchone()[0]
        )
    return int(
        conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1 AND id != ?",
            (exclude_id,),
        ).fetchone()[0]
    )


def admin_create_user(
    username: str,
    password: str,
    role: str,
    display_name: str,
    *,
    is_active: bool,
    supervised_by_id: Optional[int] = None,
) -> Tuple[bool, str]:
    if role not in VALID_ROLES:
        return False, "Invalid role."
    u = username.strip().lower()
    if not _USERNAME_RE.match(u):
        return False, "Username: 3–64 chars, letters, digits, . _ -"
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    dn = (display_name or u).strip() or u
    salt, ph = _hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    sb = supervised_by_id if role == "student" else None
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO users (username, password_salt, password_hash, role, display_name, is_active, created_at, supervised_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (u, salt, ph, role, dn, 1 if is_active else 0, now, sb),
        )
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def admin_set_active(user_id: int, active: bool, actor_id: int) -> Tuple[bool, str]:
    conn = _connect()
    try:
        row = conn.execute("SELECT role, is_active FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return False, "User not found."
        if int(row["is_active"]) == (1 if active else 0):
            return True, ""
        if not active and row["role"] == "admin":
            if count_active_admins_except(conn, user_id) < 1:
                return False, "Cannot deactivate the last active administrator."
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if active else 0, user_id))
        conn.commit()
        return True, ""
    finally:
        conn.close()


def admin_set_role(user_id: int, new_role: str, actor_id: int) -> Tuple[bool, str]:
    if new_role not in VALID_ROLES:
        return False, "Invalid role."
    conn = _connect()
    try:
        row = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return False, "User not found."
        old = row["role"]
        if old == "admin" and new_role != "admin":
            if count_active_admins_except(conn, user_id) < 1:
                return False, "Cannot remove the last administrator."
        if new_role != "student":
            conn.execute("UPDATE users SET supervised_by = NULL WHERE id = ?", (user_id,))
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()
        return True, ""
    finally:
        conn.close()


def admin_approve_user(
    user_id: int,
    role: str,
    actor_id: int,
    *,
    supervised_by_id: Optional[int] = None,
) -> Tuple[bool, str]:
    if role not in ("instructor", "student"):
        return False, "Approval role must be instructor or student."
    conn = _connect()
    try:
        if conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is None:
            return False, "User not found."
        sb = supervised_by_id if role == "student" else None
        conn.execute(
            "UPDATE users SET is_active = 1, role = ?, supervised_by = ? WHERE id = ?",
            (role, sb, user_id),
        )
        conn.commit()
        return True, ""
    finally:
        conn.close()


def admin_set_supervised_by(student_id: int, supervisor_id: Optional[int], actor_id: int) -> Tuple[bool, str]:
    conn = _connect()
    try:
        stu = conn.execute("SELECT role FROM users WHERE id = ?", (student_id,)).fetchone()
        if stu is None or stu["role"] != "student":
            return False, "Target must be a student account."
        if supervisor_id is not None:
            sup = conn.execute(
                "SELECT role, is_active FROM users WHERE id = ?",
                (supervisor_id,),
            ).fetchone()
            if sup is None or not int(sup["is_active"]):
                return False, "Supervisor not found or inactive."
            if sup["role"] != "instructor":
                return False, "Supervisor must be an active instructor account."
        conn.execute(
            "UPDATE users SET supervised_by = ? WHERE id = ?",
            (supervisor_id, student_id),
        )
        conn.commit()
        return True, ""
    finally:
        conn.close()


def admin_reset_password(user_id: int, new_password: str, actor_id: int) -> Tuple[bool, str]:
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters."
    salt, ph = _hash_password(new_password)
    conn = _connect()
    try:
        if conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is None:
            return False, "User not found."
        conn.execute(
            "UPDATE users SET password_salt = ?, password_hash = ? WHERE id = ?",
            (salt, ph, user_id),
        )
        conn.commit()
        return True, ""
    finally:
        conn.close()


def set_password_for_username(username: str, new_password: str) -> Tuple[bool, str]:
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters."
    u = username.strip().lower()
    salt, ph = _hash_password(new_password)
    conn = _connect()
    try:
        cur = conn.execute(
            "UPDATE users SET password_salt = ?, password_hash = ? WHERE username = ?",
            (salt, ph, u),
        )
        if cur.rowcount == 0:
            return False, "User not found."
        conn.commit()
        return True, ""
    finally:
        conn.close()


def admin_delete_user(user_id: int, actor_id: int) -> Tuple[bool, str]:
    if user_id == actor_id:
        return False, "You cannot delete your own account."
    conn = _connect()
    try:
        row = conn.execute("SELECT role, is_active FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return False, "User not found."
        if row["role"] == "admin" and int(row["is_active"]):
            if count_active_admins_except(conn, user_id) < 1:
                return False, "Cannot delete the last active administrator."
        conn.execute("UPDATE users SET supervised_by = NULL WHERE supervised_by = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True, ""
    finally:
        conn.close()
