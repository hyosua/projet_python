import os
import pickle
import tempfile
import time
import hashlib
import threading
from datetime import datetime
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash
from schemas import User, Question, PublicLink, Attempt

BASE = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(BASE, "users.pickle")
DIR_QUESTIONS = os.path.join(BASE, "questions")
DIR_LINKS = os.path.join(BASE, "links")
DIR_ATTEMPTS = os.path.join(BASE, "attempts")

_lock = threading.Lock()


def _ensure_dirs():
    os.makedirs(BASE, exist_ok=True)
    for d in (DIR_QUESTIONS, DIR_LINKS, DIR_ATTEMPTS):
        os.makedirs(d, exist_ok=True)

_ensure_dirs()

# -------- utilitaires fichier atomique ---------------------------------------

def _atomic_dump(obj, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_")
    try:
        with os.fdopen(fd, "wb") as f:
            pickle.dump(obj, f)
        os.replace(tmp, path)
    finally:
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass

def _atomic_load(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "rb") as f:
        return pickle.load(f)

# -------- users --------------------------------------------------------------

def get_user(email: str) -> Optional[User]:
    users: dict[str, User] = _atomic_load(USERS_FILE, {})
    return users.get(email)

def create_user(email: str, password: str) -> User:
    with _lock:
        users: dict[str, User] = _atomic_load(USERS_FILE, {})
        if email in users:
            raise ValueError("email exists")
        u = User(email=email, password_hash=generate_password_hash(password))
        users[email] = u
        _atomic_dump(users, USERS_FILE)
        return u

def verify_user(email: str, password: str) -> Optional[User]:
    u = get_user(email)
    if u and check_password_hash(u.password_hash, password):
        return u
    return None

# -------- questions ----------------------------------------------------------

def _q_path(num: int) -> str:
    return os.path.join(DIR_QUESTIONS, f"{num}.pickle")

def save_question(q: Question):
    q.updated_at = datetime.utcnow()
    _atomic_dump(q, _q_path(q.num))

def load_question(num: int) -> Optional[Question]:
    p = _q_path(num)
    if not os.path.exists(p):
        return None
    return _atomic_load(p, None)

def list_questions_by_owner(email: str) -> list[Question]:
    out: list[Question] = []
    for fname in os.listdir(DIR_QUESTIONS):
        if not fname.endswith(".pickle"):
            continue
        q: Question = _atomic_load(os.path.join(DIR_QUESTIONS, fname), None)
        if q and q.owner_email == email:
            out.append(q)
    return sorted(out, key=lambda x: x.num)

# -------- liens publics ------------------------------------------------------

def _l_path(code: str) -> str:
    return os.path.join(DIR_LINKS, f"{code}.pickle")

def create_link(question_num: int) -> PublicLink:
    code = hashlib.sha1(f"{question_num}-{time.time()}".encode()).hexdigest()[:10]
    link = PublicLink(code=code, question_num=question_num)
    _atomic_dump(link, _l_path(code))
    return link

def load_link(code: str) -> Optional[PublicLink]:
    p = _l_path(code)
    if not os.path.exists(p):
        return None
    return _atomic_load(p, None)

# -------- tentatives ---------------------------------------------------------

def save_attempt(a: Attempt):
    qdir = os.path.join(DIR_ATTEMPTS, str(a.question_num))
    os.makedirs(qdir, exist_ok=True)
    stamp = int(a.created_at.timestamp())
    key = hashlib.md5((a.student_email + a.answer_text).encode()).hexdigest()[:8]
    path = os.path.join(qdir, f"{stamp}__{key}.pickle")
    _atomic_dump(a, path)

def list_attempts(question_num: int) -> list[Attempt]:
    qdir = os.path.join(DIR_ATTEMPTS, str(question_num))
    if not os.path.exists(qdir):
        return []
    out: list[Attempt] = []
    for f in os.listdir(qdir):
        if f.endswith(".pickle"):
            out.append(_atomic_load(os.path.join(qdir, f), None))
    return sorted(out, key=lambda a: a.created_at)
