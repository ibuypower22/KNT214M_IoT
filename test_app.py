import os
import pytest
from app import app, camera_ids

# Pytest fixture to configure the test client
@pytest.fixture
def client():
    app.testing = True
    client = app.test_client()
    yield client
    # Cleanup after tests
    camera_ids.clear()
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        for file in os.listdir(upload_folder):
            os.remove(os.path.join(upload_folder, file))

# Test the index route
def test_serve_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data  # index.html starts with this

# Test adding a camera
def test_add_camera(client):
    response = client.post('/api/addcamera', json={"id": "camera1"})
    assert response.status_code == 200
    assert response.json == {"status": "Camera added", "camera_id": "camera1"}

    # Test adding the same camera again
    response = client.post('/api/addcamera', json={"id": "camera1"})
    assert response.status_code == 400
    assert response.json["message"] == "Camera ID already exists"

# Test deleting a camera
def test_delete_camera(client):
    client.post('/api/addcamera', json={"id": "camera2"})

    # Delete existing camera
    response = client.post('/api/deletecamera', json={"id": "camera2"})
    assert response.status_code == 200
    assert response.json == {"status": "Camera deleted", "camera_id": "camera2"}

    # Try deleting a non-existent camera
    response = client.post('/api/deletecamera', json={"id": "camera3"})
    assert response.status_code == 404
    assert response.json["message"] == "Camera ID not found"

# Test getting available cameras
def test_get_cameras(client):
    client.post('/api/addcamera', json={"id": "camera4"})
    response = client.get('/api/getcameras')
    assert response.status_code == 200
    assert "camera4" in response.json["available_cameras"]