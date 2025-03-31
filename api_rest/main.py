from flask import Flask, request, jsonify
import requests
import math

# Base URL of the legacy ERP API
LEGACY_ERP_BASE_URL = (
    "https://cdn.nuwe.io/challenges-ds-datasets/hackathon-schneider-erp"
)
app = Flask(__name__)


# Retrieve product details from the legacy ERP
@app.route("/api/products", methods=["GET"])
def get_product():
    """
    Endpoint to fetch information about a specific product.
    Parameters:
        part_id: ID of the part to be queried
    Returns:
        JSON containing product details including id, type, stock, and status
    """
    try:
        part_id = request.args.get("part_id")

        if not part_id:
            return jsonify({"error": "Parameter 'part_id' is required"}), 400

        part_url = f"{LEGACY_ERP_BASE_URL}/parts/{part_id}"
        part_response = requests.get(part_url)

        if part_response.status_code != 200:
            return jsonify({"error": f"Product with ID {part_id} not found"}), 500

        part_data = part_response.json()

        product_type = part_data.get("type")
        stock_url = f"{LEGACY_ERP_BASE_URL}/stock/{product_type}"
        stock_response = requests.get(stock_url)

        if stock_response.status_code != 200:
            return jsonify({"error": f"Stock for type {product_type} not found"}), 500

        stock_data = stock_response.json()

        response = {
            "id": int(part_id),
            "type": part_data.get("type"),
            "stock": stock_data.get("stock"),
            "status": part_data.get("status")
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


# Calculate distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on Earth using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of the first point (in degrees)
        lat2, lon2: Latitude and longitude of the second point (in degrees)

    Returns:
        Distance in kilometers between the two points
    """
    r = 6371.0  # Earth's radius in km

    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


# Get the 2 nearest technicians
@app.route("/api/technicians/nearest", methods=["GET"])
def get_nearest_technicians():
    """
    Endpoint to fetch the two nearest technicians to a specific location.
    Parameters:
        lat: Latitude of the location
        lon: Longitude of the location
    Returns:
        JSON list containing the two closest technicians
    """
    try:
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Parameters 'lat' and 'lon' are required"}), 400

        try:
            lat, lon = float(lat), float(lon)
        except ValueError:
            return jsonify({"error": "Coordinates 'lat' and 'lon' must be valid numbers"}), 400

        technicians_url = f"{LEGACY_ERP_BASE_URL}/technicians/available"
        response = requests.get(technicians_url)

        if response.status_code != 200:
            return jsonify({"error": "Unable to retrieve technician list"}), 500

        technicians = response.json()

        technicians_with_distance = [
            {
                "id": int(tech["id"]),
                "name": tech["name"],
                "distance_km": round(haversine(lat, lon, float(tech["latitude"]), float(tech["longitude"])), 2)
            }
            for tech in technicians
        ]

        technicians_with_distance.sort(key=lambda x: x["distance_km"])

        return jsonify(technicians_with_distance[:2]), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
