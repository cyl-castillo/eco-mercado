"""HTTP server for Mercado Circular with basic API and token-based security.

This script uses only the Python standard library to implement a minimal
web server supporting a JSON API and serving static files for the
frontend. It includes basic security measures: POST requests to
create new products require an API token supplied in the Authorization
header. Input is sanitised and validated to mitigate simple injection
attacks.

To run the server:

    python3 server.py

The server will listen on http://localhost:8000 by default.
"""

import json
import os
import html
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


# Configure the API token for write operations. In a production
# deployment this token should be stored securely (e.g. environment
# variable). For simplicity it's hardcoded here. Clients must send
# the token as an Authorization header: 'Bearer <API_TOKEN>'.
API_TOKEN = os.environ.get('API_TOKEN', 'changeme-token')

# Paths to data and static files
BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def load_products() -> list:
    """Load products from the JSON file, returning an empty list if not found."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_products(products: list) -> None:
    """Persist products to the JSON file, creating directories as needed."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


class CircularHandler(SimpleHTTPRequestHandler):
    """Request handler that serves API endpoints and static files."""

    # Override the directory for static files
    def translate_path(self, path: str) -> str:
        """Map URIs to filesystem paths for static content."""
        # Serve API routes from memory; others from static directory
        parsed = urlparse(path)
        if parsed.path.startswith('/api/'):
            # Return dummy path for API so static file serving is skipped
            return path
        # Default file for root
        if parsed.path == '/':
            path = '/index.html'
        # Build full path under static directory
        filepath = os.path.join(STATIC_DIR, parsed.path.lstrip('/'))
        return filepath

    def end_headers(self) -> None:
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == '/api/products':
            self._handle_get_products()
            return
        elif parsed.path == '/api/repairs':
            self._handle_get_repairs()
            return
        # For non-API paths, delegate to the parent class which serves static files
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == '/api/products':
            self._handle_post_product()
            return
        # Unhandled POST route
        self.send_response(404)
        self.end_headers()

    def _handle_get_products(self) -> None:
        products = load_products()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(products).encode('utf-8'))

    def _handle_get_repairs(self) -> None:
        repairs = [
            {
                'name': 'Reparación de teléfonos',
                'description': 'Cambio de pantallas, baterías y puertos para smartphones y tablets.',
                'contact': 'reparasmart@example.com'
            },
            {
                'name': 'Costurera y sastrería',
                'description': 'Arreglos de ropa, ajustes y dobladillos con acabados profesionales.',
                'contact': 'costurera@example.com'
            },
            {
                'name': 'Carpintero',
                'description': 'Reparación y restauración de muebles de madera, sillas y mesas.',
                'contact': 'carpintero@example.com'
            }
        ]
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(repairs).encode('utf-8'))

    def _handle_post_product(self) -> None:
        # Validate API token
        auth = self.headers.get('Authorization', '')
        token = auth.replace('Bearer ', '') if auth.startswith('Bearer ') else None
        if token != API_TOKEN:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode('utf-8'))
            return
        # Read and parse JSON body
        length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(length)
        try:
            data = json.loads(raw_body.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
            return
        required = {'name', 'description', 'category', 'price'}
        if not required.issubset(data.keys()):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode('utf-8'))
            return
        # Sanitize inputs
        name = html.escape(str(data['name']))[:100]
        description = html.escape(str(data['description']))[:500]
        category = html.escape(str(data['category']))[:50]
        try:
            price = float(data['price'])
        except Exception:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid price'}).encode('utf-8'))
            return
        image = html.escape(str(data.get('image', '')))[:200]
        products = load_products()
        product = {
            'id': len(products) + 1,
            'name': name,
            'description': description,
            'category': category,
            'price': price,
            'image': image
        }
        products.append(product)
        save_products(products)
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'Producto agregado', 'product': product}).encode('utf-8'))


def run(port: int = 8000) -> None:
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    httpd = HTTPServer(('', port), CircularHandler)
    print(f"Servidor ejecutándose en http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == '__main__':
    # Inicializar archivo de productos con algunos ejemplos si está vacío
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
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
            }
        ]
        save_products(example_products)
    run()