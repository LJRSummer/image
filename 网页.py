import os
from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import imagehash
import itertools
from werkzeug.utils import secure_filename

# 用绝对路径确保uploads目录正确
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_hash(image_path):
    with Image.open(image_path) as img:
        return imagehash.phash(img)

def calc_similarity_score(hash1, hash2, hash_size=64):
    distance = abs(hash1 - hash2)
    return 1 - distance / hash_size

def group_similarity_score(image_folder):
    image_files = [f for f in os.listdir(image_folder) if allowed_file(f)]
    hashes = [get_image_hash(os.path.join(image_folder, f)) for f in image_files]
    scores = []
    max_pair = (None, None)
    max_score = -1
    for i, hash1 in enumerate(hashes):
        for j in range(i + 1, len(hashes)):
            hash2 = hashes[j]
            score = calc_similarity_score(hash1, hash2)
            scores.append(score)
            if score > max_score:
                max_score = score
                max_pair = (image_files[i], image_files[j])
    if not scores:
        return 0, 0, 0, (None, None)
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    return avg_score, max_score, min_score, max_pair

@app.route('/', methods=['GET', 'POST'])
def index():
    avg_score = max_score = min_score = None
    img_files = []
    max_pair = (None, None)
    if request.method == 'POST':
        # 上传前清空uploads目录，实现覆盖
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path) and allowed_file(f):
                os.remove(file_path)
        files = request.files.getlist('images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        avg_score, max_score, min_score, max_pair = group_similarity_score(UPLOAD_FOLDER)
        img_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    else:
        img_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    return render_template('index.html',
                           avg_score=avg_score,
                           max_score=max_score,
                           min_score=min_score,
                           img_files=img_files,
                           max_pair=max_pair)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)