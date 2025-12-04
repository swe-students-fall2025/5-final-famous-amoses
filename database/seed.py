import os
import sys
import time
from app_db import connect_db, seed_db
from dotenv import load_dotenv

# Load .env explicitly 
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "course_planner")
WAIT = int(os.getenv("WAIT_BEFORE_CONNECT", "2"))
ENV = os.getenv("ENVIRONMENT", "development")

if WAIT:
    time.sleep(WAIT)

try:
    db = connect_db(MONGO_URI, DB_NAME)
except Exception as e:
    print("Failed to connect to MongoDB:", e)
    sys.exit(1)

result = seed_db(db, environment=ENV)
print("Seed complete:", result)
