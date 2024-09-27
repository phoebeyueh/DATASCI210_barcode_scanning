from flask import Flask, request, render_template
from PIL import Image
from pyzbar.pyzbar import decode
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  

# Upload folder for images
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected!', 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # decoding barcode
        image = Image.open(file_path)
        decoded_barcode = decode(image)

        # barcode results 
        output = []
        for obj in decoded_barcode:
            output.append({
                'Detected Barcode': obj.data.decode('utf-8'),
                'Type': obj.type
            })

        return render_template('result.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)