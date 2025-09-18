from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import base64
import os
import json

app = Flask(__name__)
# Use env vars if available, otherwise fall back to the same values you had
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'NEERU')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:admin@localhost:1221/testdb'


)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------
# User Model
# ------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed

with app.app_context():
    db.create_all()

# ------------------------------
# Token generation
# ------------------------------
def generate_token(user, hours=1):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    # PyJWT can return bytes in older versions — ensure string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

# ------------------------------
# Helpers: base64url decode & parse JWT without verification
# ------------------------------
def _b64url_decode(data: str) -> bytes:
    """Base64url decode with correct padding (returns bytes)."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    rem = len(data) % 4
    if rem:
        data += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(data)

def decode_jwt_unverified(token: str):
    """Return (header_dict, payload_dict, signature_b64url) without verifying signature."""
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Token must have exactly 3 parts separated by dots.')
    h_b64, p_b64, s_b64 = parts
    header = json.loads(_b64url_decode(h_b64))
    payload = json.loads(_b64url_decode(p_b64))
    return header, payload, s_b64  # signature left as base64url string

# ------------------------------
# Routes
# ------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    if not email or not name or not password:
        return jsonify({'message': 'Email, name and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409
    hashed = generate_password_hash(password)
    user = User(email=email, name=name, password=hashed)
    db.session.add(user)
    db.session.commit()
    token = generate_token(user)
    return jsonify({'message': 'User registered successfully', 'token': token})

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = generate_token(user)
    return jsonify({'message': 'Login successful', 'token': token})

@app.route('/decode', methods=['GET', 'POST'])
def decode_route():
    """
    Decode header & payload with signature verification.
    Accepts:
      - Authorization: Bearer <token>
      - JSON body: { "token": "<token>" }
      - Query param: ?token=<token>
    """
    token = _extract_token_from_request(request)
    if not token:
        return jsonify({'message': 'No token provided. Use Authorization: Bearer <token>, JSON {"token":...} or ?token=...'}), 400
    try:
        # Verify signature & expiry
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        header = jwt.get_unverified_header(token)
        return jsonify({
            'verified': True,
            'header': header,
            'payload': payload
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'verified': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({'verified': False, 'message': 'Invalid token', 'error': str(e)}), 401

@app.route('/verify', methods=['GET', 'POST'])
def verify_route():
    """
    Verify token signature & expiry using SECRET_KEY.
    Accepts same ways as /decode.
    """
    token = _extract_token_from_request(request)
    if not token:
        return jsonify({'message': 'No token provided.'}), 400
    try:
        # This will raise ExpiredSignatureError or InvalidTokenError on problems
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        # header can be obtained without verifying again:
        header = jwt.get_unverified_header(token)
        return jsonify({'verified': True, 'header': header, 'payload': payload})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({'message': 'Invalid token', 'error': str(e)}), 401

def _extract_token_from_request(req):
    # Authorization header first
    auth = req.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    # JSON body
    if req.is_json:
        t = req.json.get('token')
        if t:
            return t.strip()
    # Query param
    t = req.args.get('token')
    if t:
        return t.strip()
    return None

# (Optional) get all users - useful for debug (protect in prod)
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'email': u.email, 'name': u.name} for u in users])

if __name__ == '__main__':
    app.run(debug=True)