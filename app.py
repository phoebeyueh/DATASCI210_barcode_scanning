from flask import Flask, request, render_template
from PIL import Image
from pyzbar.pyzbar import decode
import os
import pandas as pd
from tabulate import tabulate

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Folder for image uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load OpenFoodFacts local data
df_us = pd.read_excel('/Users/phoebeyueh/Desktop/openfoodfacts_us.xlsx')

def is_safe_to_consume(matched_products, selected_allergens):
    unsafe_allergens = []
    
    for allergen in selected_allergens:
        # Check if the allergen is present in the matched products
        if matched_products['allergens'].str.contains(allergen, na=False).any():
            unsafe_allergens.append(allergen)

    if unsafe_allergens:
        return f"Not Safe to Consume (contains: {', '.join(unsafe_allergens)})"
    else:
        return "Safe to Consume"

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

        # Decoding barcode
        image = Image.open(file_path)
        decoded_barcode = decode(image)

        if decoded_barcode:
            decoded_barcode = decoded_barcode[0].data.decode('utf-8')
            print(f'Decoded Barcode: {decoded_barcode}')

            # Database matching
            matched_products = df_us[df_us['code'].astype(str).str.contains(decoded_barcode)]
            if len(matched_products.index) > 0:
                print("Matched Product Information:")
                output = matched_products[['url', 'product_name', 'ingredients_text']]
                print(tabulate(output, headers='keys', tablefmt='psql'))

                # Get user inputs for allergen selection
                selected_allergens = request.form.getlist('allergens')
                print(f"Selected Allergens: {selected_allergens}")

                # Check if users can consume the product
                safety_status = is_safe_to_consume(matched_products, selected_allergens)
                print(safety_status)

                return render_template('result.html', output=output.to_dict(orient='records'), safety_status=safety_status)
            else:
                print("No matching product found.")
                return render_template('result.html', output=[], safety_status="No matching product found.")
        else:
            print("No barcodes detected in the image.")
            return render_template('result.html', output=[], safety_status="No barcodes detected in the image.")

if __name__ == '__main__':
    app.run(debug=True)