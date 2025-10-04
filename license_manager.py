import os, json, requests, datetime, base64

DATA_DIR = os.path.join("data", "steam_rental")
os.makedirs(DATA_DIR, exist_ok=True)

LICENSE_FILE = os.path.join(DATA_DIR, "active_key.json")
LICENSES_URL = "https://raw.githubusercontent.com/Josu2003/steam_rental_plugin/refs/heads/main/licenses.dat"

class LicenseManager:
    def __init__(self):
        self.local_key = self.load_key()

    def load_key(self):
        if not os.path.exists(LICENSE_FILE):
            return None
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("key")
        except Exception:
            return None

    def save_key(self, key):
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump({"key": key}, f, ensure_ascii=False, indent=2)

    def is_valid(self):
        """Проверка лицензии через GitHub"""
        if not self.local_key:
            return False
        try:
            res = requests.get(LICENSES_URL, timeout=10)
            if res.status_code != 200:
                return False
            data = json.loads(base64.b64decode(res.text).decode())
            if self.local_key not in data:
                return False
            lic = data[self.local_key]
            exp = datetime.datetime.fromisoformat(lic["expires"])
            if datetime.datetime.now() > exp:
                return False
            return True
        except Exception:
            return False

    def activate_command(self, message, CARDINAL):
        """Активация ключа через команду /activate"""
        user_id = message.chat.id
        parts = message.text.strip().split(" ")
        if len(parts) < 2:
            CARDINAL.telegram.bot.send_message(
                user_id, "⚠️ Используй: /activate XXXX-XXXX-XXXX-XXXX", parse_mode="HTML"
            )
            return

        key = parts[1].strip().upper()
        try:
            res = requests.get(LICENSES_URL, timeout=10)
            if res.status_code != 200:
                CARDINAL.telegram.bot.send_message(user_id, "❌ Ошибка загрузки базы лицензий", parse_mode="HTML")
                return
            data = json.loads(base64.b64decode(res.text).decode())
        except Exception:
            CARDINAL.telegram.bot.send_message(user_id, "❌ Ошибка соединения с сервером", parse_mode="HTML")
            return

        if key not in data:
            CARDINAL.telegram.bot.send_message(user_id, "❌ Неверный ключ", parse_mode="HTML")
            return

        lic = data[key]
        exp = datetime.datetime.fromisoformat(lic["expires"])
        if datetime.datetime.now() > exp:
            CARDINAL.telegram.bot.send_message(user_id, "⏰ Срок действия истёк", parse_mode="HTML")
            return

        self.save_key(key)
        CARDINAL.telegram.bot.send_message(user_id, "✅ Лицензия активирована!", parse_mode="HTML")

