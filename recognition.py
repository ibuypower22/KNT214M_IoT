import face_recognition

def get_faces_positions(image_path):
    try: 
        # Load the image from the file system
        image = face_recognition.load_image_file(image_path)
    
        # Detect all face locations
        face_locations = face_recognition.face_locations(image, model="hog")
    
        return face_locations
    except:
        return []