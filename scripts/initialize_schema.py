# initialize_schema.py
# Updated: 2025-06-18
# By: Scott O.
# This Initializes the database schema. It creates the necessary tables and triggers for managing service requests.
import psycopg2
from db_connect import get_db_connection  # Assumes get_connection() returns a valid connection


def create_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # AppUser Table (renamed from User to AppUser to avoid conflict with Python's built-in User type)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AppUser (
                UserID SERIAL PRIMARY KEY,
                FirstName VARCHAR(50),
                LastName VARCHAR(50),
                PhoneNumber VARCHAR(15)
            );
        """)

        # Location Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Location (
                LocationID SERIAL PRIMARY KEY,
                Latitude DECIMAL(9,6),
                Longitude DECIMAL(9,6),
                City VARCHAR(50),
                ZipCode VARCHAR(10)
            );
        """)

        # RequestStatus Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RequestStatus (
                StatusID SERIAL PRIMARY KEY,
                StatusName VARCHAR(50)
            );
        """)

        # ServiceRequest Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ServiceRequest (
                RequestID SERIAL PRIMARY KEY,
                SourceRequestID VARCHAR(50) UNIQUE NOT NULL,  -- Honolulu 311 ID
                RequestType VARCHAR(100),
                Description TEXT,
                RequestDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UserID INTEGER REFERENCES AppUser(UserID),
                LocationID INTEGER REFERENCES Location(LocationID),
                StatusID INTEGER REFERENCES RequestStatus(StatusID)
            );
        """)

        # StatusChangeLog Table (for trigger logging)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS StatusChangeLog (
                LogID SERIAL PRIMARY KEY,
                RequestID INTEGER,
                OldStatusID INTEGER,
                NewStatusID INTEGER,
                ChangedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Trigger function to log status changes
        cursor.execute("""
            CREATE OR REPLACE FUNCTION log_status_change()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.StatusID <> OLD.StatusID THEN
                    INSERT INTO StatusChangeLog (RequestID, OldStatusID, NewStatusID)
                    VALUES (OLD.RequestID, OLD.StatusID, NEW.StatusID);
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Drop and recreate trigger
        cursor.execute("DROP TRIGGER IF EXISTS trg_status_change ON ServiceRequest;")
        cursor.execute("""
            CREATE TRIGGER trg_status_change
            AFTER UPDATE ON ServiceRequest
            FOR EACH ROW
            WHEN (OLD.StatusID IS DISTINCT FROM NEW.StatusID)
            EXECUTE FUNCTION log_status_change();
        """)

        conn.commit()
        print("Schema created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_schema()
