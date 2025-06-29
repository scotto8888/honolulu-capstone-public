# Updated: 2025-06-23
# By: Scott O.
# File: ingestion/db_connect.py
# Purpose: Establish database connection for ingestion service

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise EnvironmentError("DATABASE_URL environment variable not set")

        conn = psycopg2.connect(
            dsn=database_url,
            cursor_factory=RealDictCursor
        )
        return conn

    except Exception as e:
        print("Database connection failed:", str(e))
        sys.exit(1)  # Exit immediately with failure if DB connection fails
