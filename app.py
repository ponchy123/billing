from flask import Flask, request, jsonify
from functools import wraps
import jwt
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')  # In production, use proper secret key

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/products', methods=['GET'])
@token_required
def get_products():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    
    # Mock product data
    products = [
        {"id": 1, "name": "Product 1", "code": "P001"},
        {"id": 2, "name": "Product 2", "code": "P002"}
    ]
    
    return jsonify({"products": products}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
