import os
import random
import base64
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ad', methods=['GET'])
def get_ad():
    src_dir = './src'
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    all_files = os.listdir(src_dir)

    image_files = [f for f in all_files if not f.endswith('.txt')]

    if not image_files:
        return jsonify({"error": "No image files found"}), 404

    image_file = random.choice(image_files)
    image_path = os.path.join(src_dir, image_file)

    base_name = os.path.splitext(image_file)[0]

    link_file = base_name + '.txt'
    link_path = os.path.join(src_dir, link_file)

    if not os.path.exists(link_path):
        return jsonify({"error": f"Link file {link_file} not found"}), 404

    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')

    with open(link_path, 'r') as link_file:
        link = link_file.read().strip()

    return jsonify({
        "image": img_base64,
        "link": link
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)