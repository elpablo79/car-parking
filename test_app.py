import pytest
from app import app, users, parking_lot, bcrypt
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    # Login e ottieni il token JWT
    response = client.post('/login', 
        json={'username': 'admin', 'password': 'password'})
    token = json.loads(response.data)['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_login_success(client):
    response = client.post('/login',
        json={'username': 'admin', 'password': 'password'})
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)

def test_login_failure(client):
    response = client.post('/login',
        json={'username': 'admin', 'password': 'wrong_password'})
    assert response.status_code == 401

def test_park_car(client, auth_headers):
    # Test parcheggio riuscito
    response = client.post('/park',
        json={'license_plate': 'ABC123'},
        headers=auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['license_plate'] == 'ABC123'
    assert 'slot' in data

    # Test parcheggio pieno
    for i in range(len(parking_lot)-1):
        client.post('/park',
            json={'license_plate': f'TEST{i}'},
            headers=auth_headers)
    response = client.post('/park',
        json={'license_plate': 'XYZ789'},
        headers=auth_headers)
    assert response.status_code == 400

def test_get_slot(client, auth_headers):
    # Reset dello stato del parcheggio
    for slot in parking_lot:
        slot['occupied'] = False
        slot['license_plate'] = None
    
    # Prepara un posto occupato e verifica che il parcheggio sia avvenuto
    response = client.post('/park',
        json={'license_plate': 'ABC123'},
        headers=auth_headers)
    assert response.status_code == 201  # Verifica che il parcheggio sia riuscito
    
    # Test slot valido occupato
    response = client.get('/slot/0', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['occupied'] == True
    assert data['license_plate'] == 'ABC123'

    # Test slot valido vuoto
    response = client.get('/slot/1', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['occupied'] == False
    assert data['license_plate'] == None

    # Test slot non valido
    response = client.get('/slot/999', headers=auth_headers)
    assert response.status_code == 400

def test_unpark_car(client, auth_headers):
    # Prepara un'auto parcheggiata
    client.post('/park',
        json={'license_plate': 'ABC123'},
        headers=auth_headers)

    # Test rimozione auto riuscita
    response = client.delete('/unpark',
        json={'license_plate': 'ABC123'},
        headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['license_plate'] == 'ABC123'

    # Test rimozione auto non trovata
    response = client.delete('/unpark',
        json={'license_plate': 'NOTFOUND'},
        headers=auth_headers)
    assert response.status_code == 404
