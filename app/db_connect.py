# Updated: 2025-06-23
# By: Scott O.
# File: app/db_connect.py
# Purpose: Establish database connection for Flask web application

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("Missing DATABASE_URL environment variable")

        conn = psycopg2.connect(
            dsn=database_url,
            cursor_factory=RealDictCursor
        )
        return conn

    except Exception as e:
        print("Database connection failed:", str(e))
        return None