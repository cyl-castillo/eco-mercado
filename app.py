"""Flask backend for the Mercado Circular MVP.

This simple server provides REST API endpoints to manage products and
repair services and serves the static frontend files. It stores
products in a JSON file on disk to persist between restarts. The
endpoints are designed for demonstration purposes and do not include
authentication or input validation beyond basic checks.

Run this app with `python app.py` and then open
http://localhost:5000 in your browser.
"""

import json
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


# Initialize the Flask application. The static folder is set to the
# current directory so it can serve our HTML, CSS and JS files
# directly. static_url_path is set to empty string so the root URL
# maps to the index.html file.
app = Flask(__name__, static_folder='.', static_url_path='')

# Enable Cross Origin Resource Sharing so that the frontend can fetch
# data from the API endpoints when running directly from the file
# system or from another domain during development.
CORS(app)

# Path to the JSON file used to persist products. This file is
# relative to the application's directory.
DATA_FILE = os.path.join(os.path.dirname(__file__), 'products.json')


def load_products() -> list:
    """Load the list of products from the data file.

    Returns an empty list if the file does not exist or is empty.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is malformed, ignore and start fresh
            return []
    return []


def save_products(products: list) -> None:
    """Save the list of products to the data file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


@app.route('/api/products', methods=['GET'])
def get_products() -> tuple:
    """Return the list of products as JSON."""
    products = load_products()
    return jsonify(products)


@app.route('/api/products', methods=['POST'])
def add_product() -> tuple:
    """Add a new product to the list.

    Expects JSON data with at least name, description, category and
    price. The image field is optional. Assigns a simple numeric
    identifier based on the current number of products.
    """
    data = request.get_json() or {}
    # Basic validation of required fields
    required_fields = {'name', 'description', 'category', 'price'}
    if not required_fields.issubset(data.keys()):
        return jsonify({'error': 'Missing required fields'}), 400
    products = load_products()
    # Assign an ID. Use length+1 to keep simple incremental ids.
    data['id'] = len(products) + 1
    # Ensure price is stored as a float
    try:
        data['price'] = float(data['price'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    # Default image placeholder if none provided
    if not data.get('image'):
        data['image'] = ''
    products.append(data)
    save_products(products)
    return jsonify({'message': 'Producto agregado', 'product': data}), 201


@app.route('/api/repairs', methods=['GET'])
def get_repairs() -> tuple:
    """Return a static list of repair services."""
    repairs = [
        {
            'name': 'Reparación de teléfonos',
            'description': 'Servicio especializado en reparación de smartphones y tablets: cambio de pantallas, baterías y puertos.',
            'contact': 'reparasmart@example.com'
        },
        {
            'name': 'Costurera y sastrería',
            'description': 'Arreglos de ropa, ajuste de prendas, cambio de cremalleras y dobladillos. Servicio rápido y de confianza.',
            'contact': 'costurera@example.com'
        },
        {
            'name': 'Carpintero',
            'description': 'Reparación y restauración de muebles de madera, sillas, mesas y armarios. Reacabados y personalización.',
            'contact': 'carpintero@example.com'
        }
    ]
    return jsonify(repairs)


# Serve the index and other static files. Because static_url_path is
# empty, Flask will look for files relative to the static_folder. If
# a route is not found here, it will attempt to find the file on
# disk automatically. These routes are defined explicitly for
# clarity.
@app.route('/')
def serve_index() -> any:
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/market.html')
def serve_market() -> any:
    return send_from_directory(app.static_folder, 'market.html')


@app.route('/sell.html')
def serve_sell() -> any:
    return send_from_directory(app.static_folder, 'sell.html')


@app.route('/repair.html')
def serve_repair() -> any:
    return send_from_directory(app.static_folder, 'repair.html')


if __name__ == '__main__':
    # Create the data file if it does not exist to avoid errors on first
    # run. Initialise with a few example products for demonstration.
    if not os.path.exists(DATA_FILE):
        example_products = [
            {
                'id': 1,
                'name': 'Chaqueta de cuero vintage',
                'description': 'Chaqueta en buen estado, talla M.',
                'category': 'ropa',
                'price': 45.0,
                'image': 'https://images.unsplash.com/photo-1497204085333-6bfcbfd9acef?auto=format&fit=crop&w=400&q=60'
            },
            {
                'id': 2,
                'name': 'Smartphone reacondicionado',
                'description': 'Teléfono inteligente reacondicionado, 64 GB de almacenamiento.',
                'category': 'electronica',
                'price': 150.0,
                'image': 'https://images.unsplash.com/photo-1512499617640-c2f999098137?auto=format&fit=crop&w=400&q=60'
            },
            {
                'id': 3,
                'name': 'Mesa de madera reciclada',
                'description': 'Mesa hecha con madera recuperada, ideal para comedor o trabajo.',
                'category': 'muebles',
                'price': 80.0,
                'image': 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=400&q=60'
            },
            {
                'id': 4,
                'name': 'Zapatillas deportivas retro',
                'description': 'Modelo clásico en buen estado, talla 42.',
                'category': 'ropa',
                'price': 30.0,
                'image': 'https://images.unsplash.com/photo-1514053026555-49d21d1127a0?auto=format&fit=crop&w=400&q=60'
            }
        ]
        save_products(example_products)
    # Run the development server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)