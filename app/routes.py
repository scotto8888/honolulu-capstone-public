# Updated: 2025-06-22
# By: Scott O.
# This file contains the routes for the Flask application.
# It handles the main page and the API endpoint for fetching service requests, with filtering support.

from flask import Blueprint, jsonify, render_template, request
from .db_connect import get_db_connection
import psycopg2.extras

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/api/requests')
def get_requests():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Fetch query parameters from frontend
        type_filter = request.args.get('type', '').lower()
        desc_filter = request.args.get('desc', '').lower()
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        # Base query
        query = """
            SELECT 
                sr.requestid, 
                sr.requesttype, 
                sr.sourcerequestid,
                sr.description,
                sr.requestdate,
                loc.latitude, 
                loc.longitude, 
                rs.statusname
            FROM ServiceRequest sr
            JOIN RequestStatus rs ON sr.statusid = rs.statusid
            JOIN Location loc ON sr.locationid = loc.locationid
            WHERE loc.latitude != 0 AND loc.longitude != 0
        """

        params = []

        # Conditional filters
        if type_filter:
            query += " AND LOWER(sr.requesttype) LIKE %s"
            params.append(f"%{type_filter}%")

        if desc_filter:
            query += " AND LOWER(sr.description) LIKE %s"
            params.append(f"%{desc_filter}%")

        if start_date:
            query += " AND sr.requestdate >= %s"
            params.append(start_date)

        if end_date:
            query += " AND sr.requestdate <= %s"
            params.append(end_date)

        # Execute filtered query
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Format GeoJSON response
        features = []
        for row in rows:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["longitude"], row["latitude"]],
                },
                "properties": {
                    "id": row["requestid"],
                    "service": row["requesttype"],
                    "status": row["statusname"],
                    "source_request_id": row["sourcerequestid"],
                    "description": row["description"],
                    "requested_datetime": row["requestdate"].isoformat() if row["requestdate"] else None
                }
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        return jsonify(geojson)

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": "Something went wrong on the server"}), 500