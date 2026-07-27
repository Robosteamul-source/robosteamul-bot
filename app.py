# -*- coding: utf-8 -*-
"""VK Callback API bot for RoboSTEAMuL.

Version 3.2
- registration asks for kindergarten NUMBER, not name;
- application is sent to administrator only after parent confirmation;
- SQLite persistence for sessions and applications;
- VK callback secret/group validation and event deduplication;
- safer phone/name/age validation;
- unique random_id for VK messages;
- configurable contacts and administrator through environment variables.
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
VK_TOKEN = os.getenv("VK_TOKEN", "").strip()
VK_SECRET = os.getenv("VK_SECRET", "").strip()
VK_CONFIRMATION_TOKEN = os.getenv("VK_CONFIRMATION_TOKEN", "").strip()
VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", "0") or 0)
ADMIN_ID = int(os.getenv("ADMIN_ID", "441534266") or 441534266)
DATABASE_PATH = os.getenv("DATABASE_PATH", "/tmp/robosteamul_bot.sqlite3")
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")
COMPANY_SITE = os.getenv("COMPANY_SITE", "https://robosteamul.com")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Наталья")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+7 (922) 014-44-94")

# Контакты, которые бот показывает родителям по команде «контакты».
CONTACTS = (
    {"name": "Наталья", "phone": "+7 (922) 014-44-94"},
    {"name": "Ксения", "phone": "+7 (904) 805-25-61"},
    {"name": "Жанна", "phone": "+7 (951) 239-86-49"},
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("robosteamul_bot")

PROGRAMS: Dict[str, Dict[str, str]] = {
    "robo_34": {
        "name": "Робототехника «РобоСТЕАМ»",
        "age": "3–4 года",
        "description": "Первое знакомство с инженерией, конструированием и логикой в игровой форме.",
    },
    "brick": {
        "name": "Робототехника «РобоСТЕАМ Брик»",
        "age": "4–5 лет",
        "description": "Конструирование, механизмы, алгоритмы и развитие инженерного мышления.",
    },
    "pro": {
        "name": "Робототехника «РобоСТЕАМ Про»",
        "age": "5–7 лет",
        "description": "Сложные модели, механизмы, программирование и подготовка к соревнованиям.",
    },
    "pro_plus": {
        "name": "Робототехника «РобоСТЕАМ Про+»",
        "age": "7–12 лет",
        "description": "Углублённая робототехника, программирование, инженерные проекты и подготовка к соревнованиям.",
    },
    "dance": {
        "name": "Хореография «СоТворяшки»",
        "age": "3–8 лет",
        "description": "Ритм, координация, осанка, сценические постановки и выступления.",
    },
    "logoped": {
        "name": "Логопед и развитие речи",
        "age": "3–7 лет",
        "description": "Диагностика речи, постановка звуков, развитие словаря и связной речи.",
    },
    "school_45": {
        "name": "Дошколёнок",
        "age": "4–5 лет",
        "description": "Развитие мышления, речи, внимания, памяти и базовых учебных навыков.",
    },
    "school_67": {
        "name": "Дошколёнок",
        "age": "6–7 лет",
        "description": "Комплексная подготовка ребёнка к школе и формирование уверенности.",
    },
}

PROGRAM_ALIASES = {
    "1": "robo_34", "робостеам": "robo_34", "робостим": "robo_34",
    "робототехника робостеам": "robo_34", "робототехника 3-4": "robo_34",
    "2": "brick", "брик": "brick", "робостеам брик": "brick", "робостим брик": "brick",
    "робототехника робостеам брик": "brick", "робототехника 4-5": "brick",
    "3": "pro", "про": "pro", "робостеам про": "pro", "робостим про": "pro",
    "робототехника робостеам про": "pro", "робототехника 5-7": "pro",
    "4": "pro_plus", "про+": "pro_plus", "про плюс": "pro_plus",
    "робостеам про+": "pro_plus", "робостеам про плюс": "pro_plus",
    "робототехника робостеам про+": "pro_plus", "робототехника 7-12": "pro_plus",
    "5": "dance", "танцы": "dance", "хореография": "dance",
    "6": "logoped", "логопед": "logoped", "речь": "logoped",
    "7": "school_45", "дошколенок 4-5": "school_45", "дошколёнок 4-5": "school_45",
    "8": "school_67", "дошколенок 6-7": "school_67", "дошколёнок 6-7": "school_67",
}

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(db_connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                step INTEGER NOT NULL DEFAULT 0,
                child_name TEXT,
                child_age INTEGER,
                kindergarten_number TEXT,
                group_number TEXT,
                parent_name TEXT,
                parent_phone TEXT,
                program_code TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                child_name TEXT NOT NULL,
                child_age INTEGER NOT NULL,
                kindergarten_number TEXT NOT NULL,
                group_number TEXT NOT NULL,
                parent_name TEXT NOT NULL,
                parent_phone TEXT NOT NULL,
                program_code TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS processed_events (
                event_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_session(user_id: int) -> Dict[str, Any]:
    with closing(db_connect()) as conn:
        row = conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        return dict(row)
    return {"user_id": user_id, "step": 0}


def save_session(user_id: int, data: Dict[str, Any]) -> None:
    fields = {
        "step": int(data.get("step", 0)),
        "child_name": data.get("child_name"),
        "child_age": data.get("child_age"),
        "kindergarten_number": data.get("kindergarten_number"),
        "group_number": data.get("group_number"),
        "parent_name": data.get("parent_name"),
        "parent_phone": data.get("parent_phone"),
        "program_code": data.get("program_code"),
        "updated_at": now_iso(),
    }
    with closing(db_connect()) as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                user_id, step, child_name, child_age, kindergarten_number,
                group_number, parent_name, parent_phone, program_code, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                step=excluded.step,
                child_name=excluded.child_name,
                child_age=excluded.child_age,
                kindergarten_number=excluded.kindergarten_number,
                group_number=excluded.group_number,
                parent_name=excluded.parent_name,
                parent_phone=excluded.parent_phone,
                program_code=excluded.program_code,
                updated_at=excluded.updated_at
            """,
            (user_id, *fields.values()),
        )
        conn.commit()


def reset_session(user_id: int) -> None:
    with closing(db_connect()) as conn:
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()


def event_already_processed(event_id: Optional[str]) -> bool:
    if not event_id:
        return False
    try:
        with closing(db_connect()) as conn:
            conn.execute(
                "INSERT INTO processed_events(event_id, processed_at) VALUES (?, ?)",
                (event_id, now_iso()),
            )
            conn.commit()
        return False
    except sqlite3.IntegrityError:
        return True


def create_application(user_id: int, session: Dict[str, Any]) -> int:
    with closing(db_connect()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications (
                user_id, child_name, child_age, kindergarten_number, group_number,
                parent_name, parent_phone, program_code, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session["child_name"],
                int(session["child_age"]),
                session["kindergarten_number"],
                session["group_number"],
                session["parent_name"],
                session["parent_phone"],
                session["program_code"],
                now_iso(),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def validate_name(value: str) -> Tuple[bool, str]:
    value = normalize_text(value)
    if not 2 <= len(value) <= 100:
        return False, "Напишите имя длиной от 2 до 100 символов."
    if not re.fullmatch(r"[А-Яа-яЁёA-Za-z\- ]+", value):
        return False, "Используйте только буквы, пробелы и дефис."
    return True, value


def validate_age(value: str) -> Tuple[bool, str]:
    match = re.search(r"\d{1,2}", value)
    if not match:
        return False, "Напишите возраст цифрой, например: 5."
    age = int(match.group())
    if not 3 <= age <= 12:
        return False, "Сейчас программы рассчитаны на детей от 3 до 12 лет. Укажите возраст в этом диапазоне."
    return True, str(age)


def validate_kindergarten_number(value: str) -> Tuple[bool, str]:
    value = normalize_text(value)
    if value.lower() in {"нет", "не посещает", "домашний", "не ходит"}:
        return True, "Не посещает детский сад"
    match = re.search(r"\d{1,4}(?:\s*сп)?", value.lower())
    if not match:
        return False, "Напишите именно номер детского сада, например: 30, 448 или 30 СП. Если ребёнок не посещает сад — напишите «нет»."
    return True, match.group(0).upper().replace("  ", " ")


def validate_group(value: str) -> Tuple[bool, str]:
    value = normalize_text(value)
    if not value or len(value) > 80:
        return False, "Напишите номер или название группы, например: 5, «Ромашка» или «старшая»."
    return True, value


def normalize_phone(value: str) -> Tuple[bool, str]:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) == 10:
        digits = "7" + digits
    if len(digits) != 11 or not digits.startswith("7"):
        return False, "Напишите российский номер телефона, например: +7 922 123-45-67."
    formatted = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    return True, formatted


def parse_program(value: str) -> Optional[str]:
    normalized = normalize_text(value).lower().replace("ё", "е")
    if normalized in PROGRAMS:
        return normalized
    aliases = {k.replace("ё", "е"): v for k, v in PROGRAM_ALIASES.items()}
    return aliases.get(normalized)

# ---------------------------------------------------------------------------
# VK API
# ---------------------------------------------------------------------------
def vk_send(user_id: int, message: str) -> bool:
    if not VK_TOKEN:
        logger.error("VK_TOKEN is not configured")
        return False
    payload = {
        "access_token": VK_TOKEN,
        "user_id": user_id,
        "message": message,
        "random_id": secrets.randbelow(2_147_483_647) + 1,
        "v": VK_API_VERSION,
    }
    try:
        response = requests.post(
            "https://api.vk.com/method/messages.send",
            data=payload,
            timeout=(3.05, 10),
        )
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            logger.error("VK API error: %s", body["error"])
            return False
        return True
    except (requests.RequestException, ValueError) as exc:
        logger.exception("Failed to send VK message: %s", exc)
        return False

# ---------------------------------------------------------------------------
# Texts
# ---------------------------------------------------------------------------
def main_menu() -> str:
    return (
        "Здравствуйте! Я помощник центра дополнительного образования RoboSTEAMuL. 👋\n\n"
        "Помогу подобрать направление или оформить заявку:\n"
        "• напишите «программы» — узнать о направлениях;\n"
        "• напишите «запись» — записать ребёнка;\n"
        "• напишите «контакты» — связаться с администратором.\n\n"
        "Важно: свободное место и расписание подтверждает администратор."
    )


def contacts_text() -> str:
    lines = ["📞 Контакты RoboSTEAMuL", ""]
    for contact in CONTACTS:
        lines.append(f"{contact['name']}: {contact['phone']}")
    lines.extend(["", f"Сайт: {COMPANY_SITE}"])
    return "\n".join(lines)


def programs_text() -> str:
    lines = ["Программы RoboSTEAMuL:"]
    for index, program in enumerate(PROGRAMS.values(), start=1):
        lines.append(f"{index}. {program['name']} — {program['age']}\n{program['description']}")
    lines.append("\nДля записи напишите «запись». Стоимость, расписание и свободные места уточнит администратор.")
    return "\n\n".join(lines)


def program_choices() -> str:
    return (
        "Вопрос 7 из 7. Какое направление вас интересует?\n\n"
        "1 — Робототехника «РобоСТЕАМ», 3–4 года\n"
        "2 — Робототехника «РобоСТЕАМ Брик», 4–5 лет\n"
        "3 — Робототехника «РобоСТЕАМ Про», 5–7 лет\n"
        "4 — Робототехника «РобоСТЕАМ Про+», 7–12 лет\n"
        "5 — Хореография, 3–8 лет\n"
        "6 — Логопед и развитие речи, 3–7 лет\n"
        "7 — Дошколёнок, 4–5 лет\n"
        "8 — Дошколёнок, 6–7 лет\n\n"
        "Напишите цифру или название направления."
    )


def confirmation_text(session: Dict[str, Any]) -> str:
    program = PROGRAMS[session["program_code"]]
    return (
        "Проверьте заявку:\n\n"
        f"Ребёнок: {session['child_name']}\n"
        f"Возраст: {session['child_age']} лет\n"
        f"Номер детского сада: {session['kindergarten_number']}\n"
        f"Группа: {session['group_number']}\n"
        f"Родитель: {session['parent_name']}\n"
        f"Телефон: {session['parent_phone']}\n"
        f"Направление: {program['name']} ({program['age']})\n\n"
        f"Напишите «да», чтобы отправить заявку администратору {ADMIN_NAME}.\n"
        "Напишите «сначала», чтобы заполнить заново, или «отмена»."
    )


def admin_application_text(application_id: int, user_id: int, session: Dict[str, Any]) -> str:
    program = PROGRAMS[session["program_code"]]
    return (
        f"🔔 Новая заявка №{application_id}\n\n"
        f"Ребёнок: {session['child_name']}\n"
        f"Возраст: {session['child_age']} лет\n"
        f"Детский сад №: {session['kindergarten_number']}\n"
        f"Группа: {session['group_number']}\n"
        f"Родитель: {session['parent_name']}\n"
        f"Телефон: {session['parent_phone']}\n"
        f"Направление: {program['name']} ({program['age']})\n"
        f"VK ID: {user_id}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        "Нужно связаться с родителем и подтвердить расписание, стоимость и наличие места."
    )

# ---------------------------------------------------------------------------
# Dialogue
# ---------------------------------------------------------------------------
def start_registration(user_id: int) -> None:
    session = {"user_id": user_id, "step": 1}
    save_session(user_id, session)
    vk_send(
        user_id,
        "Начинаем оформление заявки. Всего 7 вопросов.\n\n"
        "Вопрос 1 из 7. Напишите фамилию и имя ребёнка.\n"
        "Например: Петров Иван.\n\n"
        "Для выхода напишите «отмена».",
    )


def process_registration(user_id: int, text: str, session: Dict[str, Any]) -> None:
    msg = normalize_text(text)
    low = msg.lower()
    if low in {"отмена", "отменить", "стоп"}:
        reset_session(user_id)
        vk_send(user_id, "Оформление заявки отменено. Чтобы начать заново, напишите «запись».")
        return

    step = int(session.get("step", 0))

    if step == 1:
        ok, value = validate_name(msg)
        if not ok:
            vk_send(user_id, f"Не удалось принять имя. {value}")
            return
        session["child_name"] = value
        session["step"] = 2
        reply = "Вопрос 2 из 7. Сколько полных лет ребёнку? Напишите цифру, например: 5."

    elif step == 2:
        ok, value = validate_age(msg)
        if not ok:
            vk_send(user_id, value)
            return
        session["child_age"] = int(value)
        session["step"] = 3
        reply = (
            "Вопрос 3 из 7. Напишите НОМЕР детского сада, который посещает ребёнок.\n"
            "Например: 30, 448 или 30 СП.\n"
            "Если ребёнок не посещает детский сад — напишите «нет»."
        )

    elif step == 3:
        ok, value = validate_kindergarten_number(msg)
        if not ok:
            vk_send(user_id, value)
            return
        session["kindergarten_number"] = value
        session["step"] = 4
        reply = (
            "Вопрос 4 из 7. Напишите номер или название группы ребёнка в детском саду.\n"
            "Например: 5, «Ромашка», «средняя». Если группы нет — напишите «нет»."
        )

    elif step == 4:
        ok, value = validate_group(msg)
        if not ok:
            vk_send(user_id, value)
            return
        session["group_number"] = value
        session["step"] = 5
        reply = "Вопрос 5 из 7. Напишите фамилию и имя родителя или законного представителя."

    elif step == 5:
        ok, value = validate_name(msg)
        if not ok:
            vk_send(user_id, f"Не удалось принять имя родителя. {value}")
            return
        session["parent_name"] = value
        session["step"] = 6
        reply = "Вопрос 6 из 7. Напишите номер телефона для связи, например: +7 922 123-45-67."

    elif step == 6:
        ok, value = normalize_phone(msg)
        if not ok:
            vk_send(user_id, value)
            return
        session["parent_phone"] = value
        session["step"] = 7
        reply = program_choices()

    elif step == 7:
        code = parse_program(msg)
        if not code:
            vk_send(user_id, "Не удалось определить направление.\n\n" + program_choices())
            return
        session["program_code"] = code
        session["step"] = 8
        save_session(user_id, session)
        vk_send(user_id, confirmation_text(session))
        return

    elif step == 8:
        if low in {"да", "да!", "подтверждаю", "верно", "отправить"}:
            application_id = create_application(user_id, session)
            admin_sent = vk_send(ADMIN_ID, admin_application_text(application_id, user_id, session))
            reset_session(user_id)
            if admin_sent:
                vk_send(
                    user_id,
                    f"✅ Заявка №{application_id} отправлена администратору {ADMIN_NAME}. "
                    "Администратор свяжется с вами, чтобы подтвердить расписание, стоимость и наличие места.\n\n"
                    + contacts_text(),
                )
            else:
                vk_send(
                    user_id,
                    f"Заявка №{application_id} сохранена, но автоматическое уведомление администратору не отправилось. "
                    "Пожалуйста, свяжитесь с одним из администраторов.\n\n" + contacts_text(),
                )
            return
        if low in {"сначала", "заново", "нет", "исправить"}:
            start_registration(user_id)
            return
        vk_send(user_id, "Ответьте «да», «сначала» или «отмена».")
        return

    else:
        reset_session(user_id)
        vk_send(user_id, "Сессия оформления была сброшена. Напишите «запись», чтобы начать заново.")
        return

    save_session(user_id, session)
    vk_send(user_id, reply)


def handle_message(user_id: int, text: str) -> None:
    text = normalize_text(text or "")
    if not text:
        vk_send(user_id, "Напишите сообщение текстом. Для начала можно написать «программы» или «запись».")
        return

    session = get_session(user_id)
    if int(session.get("step", 0)) > 0:
        process_registration(user_id, text, session)
        return

    low = text.lower().replace("ё", "е")
    if any(word in low for word in ("запис", "регистрац", "оставить заявку")):
        start_registration(user_id)
    elif "программ" in low or "направлен" in low or "круж" in low:
        vk_send(user_id, programs_text())
    elif "контакт" in low or "телефон" in low or "администратор" in low:
        vk_send(user_id, contacts_text())
    elif low in {"привет", "здравствуйте", "добрый день", "добрый вечер", "доброе утро", "начать", "старт"}:
        vk_send(user_id, main_menu())
    elif "спасибо" in low:
        vk_send(user_id, "Пожалуйста! Для записи ребёнка напишите «запись».")
    else:
        vk_send(
            user_id,
            "Я помогу узнать о направлениях и оформить заявку.\n\n"
            "Напишите:\n"
            "• «программы» — список направлений;\n"
            "• «запись» — оформить заявку;\n"
            "• «контакты» — связаться с администратором.",
        )

# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------
def callback_is_valid(data: Dict[str, Any]) -> bool:
    if VK_SECRET and data.get("secret") != VK_SECRET:
        logger.warning("Rejected callback with invalid secret")
        return False
    if VK_GROUP_ID and int(data.get("group_id", 0) or 0) != VK_GROUP_ID:
        logger.warning("Rejected callback for invalid group_id")
        return False
    return True


@app.post("/callback")
def callback() -> Tuple[str, int]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return "ok", 200

    if not callback_is_valid(data):
        return "forbidden", 403

    event_type = data.get("type")
    if event_type == "confirmation":
        if not VK_CONFIRMATION_TOKEN:
            logger.error("VK_CONFIRMATION_TOKEN is not configured")
            return "configuration error", 500
        return VK_CONFIRMATION_TOKEN, 200

    event_id = data.get("event_id")
    if event_already_processed(event_id):
        return "ok", 200

    if event_type == "message_new":
        message = data.get("object", {}).get("message", {})
        user_id = message.get("from_id")
        text = message.get("text", "")
        # Ignore messages sent by communities or invalid senders.
        if isinstance(user_id, int) and user_id > 0:
            handle_message(user_id, text)
    elif event_type == "user_subscribed":
        user_id = data.get("object", {}).get("user_id")
        if isinstance(user_id, int) and user_id > 0:
            vk_send(user_id, main_menu())

    return "ok", 200


@app.get("/")
def index():
    return jsonify(status="ok", service="RoboSTEAMuL VK bot", version="3.1")


@app.get("/health")
def health():
    database_ok = True
    try:
        with closing(db_connect()) as conn:
            conn.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        database_ok = False
    status_code = 200 if database_ok and bool(VK_TOKEN) else 503
    return jsonify(
        status="healthy" if status_code == 200 else "degraded",
        database=database_ok,
        vk_token_configured=bool(VK_TOKEN),
        timestamp=now_iso(),
    ), status_code


@app.get("/stats")
def stats():
    # Do not expose personal data. Protect this endpoint at reverse-proxy level.
    with closing(db_connect()) as conn:
        active_sessions = conn.execute("SELECT COUNT(*) FROM sessions WHERE step > 0").fetchone()[0]
        applications = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    return jsonify(active_sessions=active_sessions, applications=applications, version="3.1")


init_db()

if __name__ == "__main__":
    missing = [
        name for name, value in {
            "VK_TOKEN": VK_TOKEN,
            "VK_CONFIRMATION_TOKEN": VK_CONFIRMATION_TOKEN,
            "VK_SECRET": VK_SECRET,
            "VK_GROUP_ID": VK_GROUP_ID,
        }.items() if not value
    ]
    if missing:
        logger.warning("Missing recommended settings: %s", ", ".join(missing))
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
