import os


def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip())


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    _load_env_file()


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    EMAIL_SENDER = os.getenv('EMAIL_SENDER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_DRY_RUN = _as_bool(os.getenv('EMAIL_DRY_RUN'), default=False)

    DATA_DIR = 'data'
    HISTORY_FILE = os.path.join(DATA_DIR, 'operation_history.csv')
    EMAIL_PREVIEW_FILE = os.path.join(DATA_DIR, 'last_email_preview.txt')
