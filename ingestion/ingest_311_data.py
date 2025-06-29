# ingest_311_data.py
# Updated: 2025-06-25 v2
# By: Scott O.

import requests
import psycopg2
import psycopg2.extras
import traceback
from datetime import datetime, UTC
from db_connect import get_db_connection

API_URL = "https://data.honolulu.gov/resource/6hui-dvrh.json?$limit=1000"

def fetch_311_data():
    print("Fetching 311 data from API...")
    response = requests.get(API_URL)
    if response.status_code == 200:
        print("Data fetched successfully.")
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []

def insert_data(records):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    total = len(records)
    inserted = 0
    updated = 0
    skipped = 0

    for record in records:
        try:
            source_request_id = str(record.get("id"))
            request_type = record.get("requesttype", "Unknown")
            description = record.get("description", "")
            request_date = record.get("datecreated", None)
            status_name = record.get("statustype", "Open").strip()
            city = record.get("city", None)
            zipcode = record.get("zipcode", None)

            location = record.get("location", {})
            try:
                lat = float(location.get("latitude"))
                lon = float(location.get("longitude"))
            except (TypeError, ValueError):
                lat, lon = None, None

            # Get or insert StatusID
            cursor.execute("SELECT StatusID FROM RequestStatus WHERE StatusName = %s;", (status_name,))
            result = cursor.fetchone()
            if result:
                new_status_id = result["statusid"]
            else:
                cursor.execute("INSERT INTO RequestStatus (StatusName) VALUES (%s) RETURNING StatusID;", (status_name,))
                new_status_id = cursor.fetchone()["statusid"]

            # Get or insert LocationID
            cursor.execute("""
                SELECT LocationID FROM Location 
                WHERE Latitude = %s AND Longitude = %s AND City = %s AND ZipCode = %s;
            """, (lat, lon, city, zipcode))
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result["locationid"]
            else:
                cursor.execute("""
                    INSERT INTO Location (Latitude, Longitude, City, ZipCode)
                    VALUES (%s, %s, %s, %s)
                    RETURNING LocationID;
                """, (lat, lon, city, zipcode))
                location_id = cursor.fetchone()["locationid"]

            user_id = 1  # Placeholder

            # Check if request already exists
            cursor.execute("""
                SELECT RequestID, StatusID FROM ServiceRequest WHERE SourceRequestID = %s;
            """, (source_request_id,))
            existing = cursor.fetchone()

            if existing:
                request_id = existing["requestid"]
                old_status_id = existing["statusid"]

                if old_status_id != new_status_id:
                    # Check if this change is already logged
                    cursor.execute("""
                        SELECT 1 FROM StatusChangeLog
                        WHERE RequestID = %s AND OldStatusID = %s AND NewStatusID = %s;
                    """, (request_id, old_status_id, new_status_id))
                    already_logged = cursor.fetchone()

                    if not already_logged:
                        cursor.execute("""
                            INSERT INTO StatusChangeLog (RequestID, OldStatusID, NewStatusID, ChangedAt)
                            VALUES (%s, %s, %s, %s);
                        """, (request_id, old_status_id, new_status_id, datetime.now(UTC)))

                    # Update the service request status
                    cursor.execute("""
                        UPDATE ServiceRequest
                        SET StatusID = %s,
                            RequestType = %s,
                            Description = %s,
                            RequestDate = %s,
                            LocationID = %s,
                            UserID = %s
                        WHERE RequestID = %s;
                    """, (new_status_id, request_type, description, request_date, location_id, user_id, request_id))
                    updated += 1
                else:
                    skipped += 1
            else:
                # New ServiceRequest
                cursor.execute("""
                    INSERT INTO ServiceRequest (
                        SourceRequestID, RequestType, Description, RequestDate, UserID, LocationID, StatusID
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING RequestID;
                """, (source_request_id, request_type, description, request_date, user_id, location_id, new_status_id))
                _ = cursor.fetchone()["requestid"]
                inserted += 1

        except Exception:
            print(f"Skipping record due to error for ID {record.get('id')}")
            print(traceback.format_exc())
            skipped += 1
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print("Ingestion complete.")
    print(f"Total records fetched: {total}")
    print(f"Inserted: {inserted}")
    print(f"Updated with status change: {updated}")
    print(f"Skipped (no change or already logged): {skipped}")

if __name__ == "__main__":
    print("Starting 311 ingestion process at", datetime.now(UTC).isoformat())
    try:
        data = fetch_311_data()
        if data:
            insert_data(data)
        else:
            print("No data to ingest.")
    except Exception:
        print("Unhandled exception during ingestion:")
        print(traceback.format_exc())