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