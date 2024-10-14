from flask import Flask, request, jsonify, send_file
import mysql.connector
from io import BytesIO

app = Flask(__name__)

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host = "us-cluster-east-01.k8s.cleardb.net",
        user = "b7cb1f42f9de35",
        passwd = "1fe32160 ",
        database = "awsk_1ad786eee72ad786380b",
    )

# API route to upload an image (POST)
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    filename = file.filename
    image_data = file.read()  # Read image as binary data
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert image into MySQL database
    cursor.execute('INSERT INTO images (filename, image) VALUES (%s, %s)', (filename, image_data))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Image '{filename}' uploaded successfully"}), 201

# API route to list all images (GET)
@app.route('/api/images', methods=['GET'])
def list_images():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT filename FROM images')
    images = cursor.fetchall()
    conn.close()
    
    filenames = [image[0] for image in images]
    return jsonify({"images": filenames}), 200

# API route to download an image by filename (GET)
@app.route('/api/download/<filename>', methods=['GET'])
def download_image(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch the image by filename
    cursor.execute('SELECT image FROM images WHERE filename = %s', (filename,))
    image_record = cursor.fetchone()
    conn.close()
    
    if image_record:
        image_data = image_record[0]  # The image data is the first column in the result
        return send_file(BytesIO(image_data), attachment_filename=filename)
    else:
        return jsonify({"error": "Image not found"}), 404

# API route to delete an image by filename (DELETE)
@app.route('/api/images/<filename>', methods=['DELETE'])
def delete_image(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if image exists
    cursor.execute('SELECT * FROM images WHERE filename = %s', (filename,))
    image_record = cursor.fetchone()
    
    if image_record:
        # Delete the image if it exists
        cursor.execute('DELETE FROM images WHERE filename = %s', (filename,))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Image '{filename}' deleted successfully"}), 200
    else:
        conn.close()
        return jsonify({"error": "Image not found"}), 404
