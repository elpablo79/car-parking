# Parking Management API System

A RESTful API built with Flask to manage a car parking system. The system includes JWT authentication, rate limiting, and automated testing.

## Technical Features

- **Framework**: Flask
- **Authentication**: JWT (JSON Web Token)
- **Rate Limiting**: Implemented to prevent API abuse
- **Password Hashing**: bcrypt for credential security
- **Testing**: pytest for automated testing
- **Configuration**: Environment variables via .env file

## System Structure

The system manages:
- User authentication
- Vehicle parking
- Slot status verification
- Vehicle removal from parking

## API Endpoints

- `POST /login` - User authentication
- `POST /park` - Park a vehicle
- `GET /slot/<id>` - Check specific slot status
- `DELETE /unpark` - Remove a vehicle from parking

## Rate Limiting

- Global limit: 100 requests/hour per IP
- Specific endpoints: 10 requests/minute per user

## Configuration

1. Create a `.env` file in the project root:

```
PARKING_LOT_SIZE=5
JWT_SECRET_KEY=your_secret_key
```

## Installation

```

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```

python app.py
```

The application will be available at `http://localhost:5000`

## Running Tests

```

# Run all tests
pytest

# Run tests with details
pytest -v

# Run tests with coverage
pytest --cov=app
```

## Test Structure

Tests cover:
- Authentication (login success/failure)
- Parking operations (park/unpark)
- Slot status verification
- Error handling

## Security

- JWT authentication for all operations (except login)
- Passwords hashed with bcrypt
- Rate limiting to prevent abuse
- Input validation for all endpoints

## Main Dependencies

- Flask
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-Limiter
- python-dotenv
- pytest (for testing)

## Development Notes

- Application uses in-memory data structures for simplicity
- For production, a persistent database is recommended
- System is configured for a limited number of parking spots (default: 5)
- Default credentials: username: "admin", password: "password"

