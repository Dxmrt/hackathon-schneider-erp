from flask import Flask

# Legacy ERP API Base URL
LEGACY_ERP_BASE_URL = (
    "https://cdn.nuwe.io/challenges-ds-datasets/hackathon-schneider-erp"
)
app = Flask(__name__)


# Fetch product details from Legacy ERP
@app.route("/api/products", methods=["GET"])
def get_product():
    pass


# Calculate the distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    pass


# Get the nearest 2 technicians
@app.route("/api/technicians/nearest", methods=["GET"])
def get_nearest_technicians():
    pass


if __name__ == "__main__":
    app.run(debug=True, port=3000)
