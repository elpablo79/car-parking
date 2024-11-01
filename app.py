from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
PARKING_LOT_SIZE = int(os.getenv("PARKING_LOT_SIZE", 5))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Configure the rate limiter
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])  # Default: 100 requests per hour per IP

# In-memory data structures
parking_lot = [
    {'occupied': False, 'license_plate': None} for _ in range(PARKING_LOT_SIZE)
]
users = {"admin": bcrypt.generate_password_hash("password").decode('utf-8')}  # Predefined user for login

# Authentication endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Verify username and password
    if username in users and bcrypt.check_password_hash(users[username], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Park a car
@app.route('/park', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")  # Rate limit to 10 requests per minute per user
def park():
    license_plate = request.json.get('license_plate')
    
    # Find the first available slot
    for slot, car in enumerate(parking_lot):
        if not car['occupied']:
            parking_lot[slot]['occupied'] = True
            parking_lot[slot]['license_plate'] = license_plate
            return jsonify({"license_plate": license_plate, "slot": slot}), 201
    
    # If no slot is available
    return jsonify({"error": "Parking lot is full"}), 400

# Check a parking slot
@app.route('/slot/<int:slot_id>', methods=['GET'])
@jwt_required()
@limiter.limit("10 per minute")  # Rate limit to 10 requests per minute per user
def get_slot(slot_id):
    # Check if the slot is within the valid range
    if 0 <= slot_id < PARKING_LOT_SIZE:
        car = parking_lot[slot_id]
        if car['occupied']:
            return jsonify({"slot": slot_id, "occupied": True, "license_plate": car['license_plate']}), 200
        else:
            return jsonify({"slot": slot_id, "occupied": False, "license_plate": None}), 200
    else:
        return jsonify({"error": "Invalid slot ID"}), 400

# Unpark a car
@app.route('/unpark', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")  # Rate limit to 10 requests per minute per user
def unpark():
    license_plate = request.json.get('license_plate')
    
    # Find the car by license plate
    for slot, car in enumerate(parking_lot):
        if car['license_plate'] == license_plate:
            parking_lot[slot]['occupied'] = False
            parking_lot[slot]['license_plate'] = None
            return jsonify({"license_plate": license_plate, "slot": slot}), 200
    
    # If the car is not found
    return jsonify({"error": "Car not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
