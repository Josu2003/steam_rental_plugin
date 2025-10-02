import requests
import json
import os
from datetime import datetime

# ССЫЛКА на keys.json (raw URL из GitHub)
KEYS_URL = "https://raw.githubusercontent.com/Josu2003/steam_rental_plugin/refs/heads/main/Users_Keys.json"

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_keys():
    """Загружает базу ключей с GitHub"""
    try:
        response = requests.get(KEYS_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception:
        return {}

def save_user_key(user_id, key):
    """Сохраняет локально ключ"""
    license_file = os.path.join(DATA_DIR, "license.json")
    data = {"user_id": user_id, "key": key}
    with open(license_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_user_key():
    """Загружает локальный ключ"""
    license_file = os.path.join(DATA_DIR, "license.json")
    if not os.path.exists(license_file):
        return None
    with open(license_file, "r", encoding="utf-8") as f:
        return json.load(f)

def is_license_valid(user_id):
    """Проверяет валидность ключа"""
    license_data = load_user_key()
    if not license_data:
        return False, "❌ Нет активированного ключа. Используй /activate КЛЮЧ"

    key = license_data.get("key")
    keys = fetch_keys()

    if key not in keys:
        return False, "❌ Ключ не найден"

    key_data = keys[key]
    expires_at = datetime.fromisoformat(key_data["expires_at"])
    if datetime.now() > expires_at:
        return False, "⏰ Срок действия ключа истёк"

    if key_data["user_id"] and key_data["user_id"] != user_id:
        return False, "🔒 Ключ активирован другим пользователем"

    return True, "✅ Лицензия активна"

def activate_key(message, CARDINAL):
    """Активация ключа через /activate"""
    parts = message.text.strip().split(" ")
    if len(parts) < 2:
        CARDINAL.telegram.bot.send_message(message.chat.id, "⚠️ Используй: /activate КЛЮЧ")
        return

    key = parts[1].strip()
    keys = fetch_keys()

    if key not in keys:
        CARDINAL.telegram.bot.send_message(message.chat.id, "❌ Ключ не найден")
        return

    key_data = keys[key]
    expires_at = datetime.fromisoformat(key_data["expires_at"])
    if datetime.now() > expires_at:
        CARDINAL.telegram.bot.send_message(message.chat.id, "⏰ Срок действия ключа истёк")
        return

    if key_data["user_id"] and key_data["user_id"] != message.chat.id:
        CARDINAL.telegram.bot.send_message(message.chat.id, "🔒 Ключ уже используется другим пользователем")
        return

    # сохраняем локально
    save_user_key(message.chat.id, key)
    CARDINAL.telegram.bot.send_message(message.chat.id, "✅ Ключ активирован. Теперь можно использовать /srent_menu")
