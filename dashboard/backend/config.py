import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

PRICE_CSV = DATA_DIR / "BrentOilPrices.csv"
EVENTS_CSV = DATA_DIR / "key_events.csv"

# Flask
DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = int(os.getenv("FLASK_PORT", "5050"))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
