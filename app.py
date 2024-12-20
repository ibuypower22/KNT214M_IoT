from flask import Flask, request, jsonify, send_from_directory, send_file, Response
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set to store available camera IDs
camera_ids = set()

# Index static file
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

# Route to add a camera (expects a JSON body)
@app.route('/api/addcamera', methods=['POST'])
def add_camera():
    data = request.json
    camera_id = data.get('id')
    
    if not camera_id:
        return jsonify({"status": "Error", "message": "Camera ID is required"}), 400
    
    if camera_id in camera_ids:
        return jsonify({"status": "Error", "message": "Camera ID already exists"}), 400
    
    camera_ids.add(camera_id)
    return jsonify({"status": "Camera added", "camera_id": camera_id}), 200

# Route to delete a camera (expects a JSON body)
@app.route('/api/deletecamera', methods=['POST'])
def delete_camera():
    data = request.json
    camera_id = data.get('id')
    
    if not camera_id:
        return jsonify({"status": "Error", "message": "Camera ID is required"}), 400
    
    if camera_id not in camera_ids:
        return jsonify({"status": "Error", "message": "Camera ID not found"}), 404
    
    camera_ids.remove(camera_id)
    
    # Delete associated image if it exists
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{camera_id}.jpg")
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return jsonify({"status": "Camera deleted", "camera_id": camera_id}), 200

# Route to get all available camera IDs
@app.route('/api/getcameras', methods=['GET'])
def get_cameras():
    return jsonify({"available_cameras": list(camera_ids)}), 200

# Route to add an image based on ID (expects JPEG in request body)
@app.route('/api/addimage/<string:id>', methods=['POST'])
def add_image(id: str):
    if id not in camera_ids:
        return jsonify({"status": "Error", "message": "Camera ID not recognized"}), 404
    
    if 'image' not in request.files:
        return jsonify({"status": "Error", "message": "No image found"}), 400
    
    image = request.files['image']
    if image.mimetype != 'image/jpeg':
        return jsonify({"status": "Error", "message": "Invalid image format, only JPEG allowed"}), 400
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{id}.jpg")
    
    # Save the image synchronously
    image.save(image_path)
    
    # Return 200 OK with no content
    return Response(status=200)

# Route to get an image based on ID
@app.route('/api/getimage/<string:id>', methods=['GET'])
def get_image(id: str):
    if id not in camera_ids:
        return jsonify({"status": "Error", "message": "Camera ID not recognized"}), 404
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{id}.jpg")
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return jsonify({"status": "Error", "message": "Image not found"}), 404

if __name__ == '__main__':
        app.run(debug=True)