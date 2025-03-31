import sqlite3
from flask import Flask, request, jsonify
import requests
import math
import logging

DB_FILE = "sql_queries/erp.db"

# Connect to SQLite database. Do not change this. Call this function within each of the requested functions.
def get_db_connection(db_file):
    return sqlite3.connect(db_file)



# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Base URL of the legacy ERP API
LEGACY_ERP_BASE_URL = (
    "https://cdn.nuwe.io/challenges-ds-datasets/hackathon-schneider-erp"
)
app = Flask(__name__)


# Helper function for making API requests
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None


# Retrieve product details from the legacy ERP
@app.route("/api/products", methods=["GET"])
def get_product():
    try:
        part_id = request.args.get("part_id")
        if not part_id:
            return jsonify({"error": "Parameter 'part_id' is required"}), 400

        part_data = fetch_data(f"{LEGACY_ERP_BASE_URL}/parts/{part_id}")
        if not part_data:
            return jsonify({"error": f"Product with ID {part_id} not found"}), 404

        stock_data = fetch_data(f"{LEGACY_ERP_BASE_URL}/stock/{part_data.get('type')}")
        if not stock_data:
            return jsonify({"error": f"Stock for type {part_data.get('type')} not found"}), 404

        return jsonify({
            "id": int(part_id),
            "type": part_data.get("type"),
            "stock": stock_data.get("stock"),
            "status": part_data.get("status")
        }), 200
    except Exception as e:
        logging.error(f"Internal error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# Calculate distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0  # Earth's radius in km
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Get the 2 nearest technicians
@app.route("/api/technicians/nearest", methods=["GET"])
def get_nearest_technicians():
    try:
        lat, lon = request.args.get("lat"), request.args.get("lon")
        if not lat or not lon:
            return jsonify({"error": "Parameters 'lat' and 'lon' are required"}), 400

        try:
            lat, lon = float(lat), float(lon)
        except ValueError:
            return jsonify({"error": "Coordinates 'lat' and 'lon' must be valid numbers"}), 400

        technicians = fetch_data(f"{LEGACY_ERP_BASE_URL}/technicians/available")
        if not technicians:
            return jsonify({"error": "Unable to retrieve technician list"}), 500

        technicians_with_distance = sorted([
            {
                "id": int(tech["id"]),
                "name": tech["name"],
                "distance_km": round(haversine(lat, lon, float(tech["latitude"]), float(tech["longitude"])), 2)
            }
            for tech in technicians
        ], key=lambda x: x["distance_km"])

        return jsonify(technicians_with_distance[:2]), 200
    except Exception as e:
        logging.error(f"Internal error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
