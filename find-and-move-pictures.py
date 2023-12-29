# Depends on VS build tools, Boost, dlib, facial_recognition, cmake, and VS C++
# Script to find pictures of someone in a directory, and move it into another directory.

import os
import shutil
import face_recognition

source_folder = "D:/Pictures"
destination_folder = "D:/temp/son1"
son_image_path = "D:/temp/son1.jpg"

# Load the image of your son
son_image = face_recognition.load_image_file(son_image_path)
son_encoding = face_recognition.face_encodings(son_image)[0]

def check_if_son_present(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)

    # Find all face locations in the image
    face_locations = face_recognition.face_locations(image)

    # If there are no faces in the image, return False
    if not face_locations:
        return False

    # Get face encodings for all faces in the image
    face_encodings = face_recognition.face_encodings(image, face_locations)

    # Check if any face matches the son's face
    for face_encoding in face_encodings:
        match = face_recognition.compare_faces([son_encoding], face_encoding)
        if any(match):
            return True

    return False

for root, dirs, files in os.walk(source_folder):
    for file in files:
        file_path = os.path.join(root, file)
        print("Kicking in that facial recognition, finding a match, and moving it to your destination . . .")
        matches = 0

        # Check if the file is an image (you may need to customize this check)
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Check if the image contains your son's face
            son_present = check_if_son_present(file_path)
            if son_present:
                # Move the file to the destination folder
                shutil.move(file_path, os.path.join(destination_folder, file))
                matches += 1

print("Process complete! Found (matches) matches. ")
