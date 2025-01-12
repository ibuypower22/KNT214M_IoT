import face_recognition

def get_faces_count(image_path):
    # Load the image from the file system
    image = face_recognition.load_image_file(image_path)
    
    # Detect all face locations
    face_locations = face_recognition.face_locations(image)
    
    return len(face_locations)