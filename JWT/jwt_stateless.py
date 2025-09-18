from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
# It successfully authenticates users without storing data,                              Users with valid credentials can obtain a  token and access  routes.
#Provides a practical example of stateless JWT usage, which can be reused in more complex authentication workflows.
app.config['SECRET_KEY'] = "NEERAJA"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Dummy username/password check
    if data and data.get("username") == "admin" and data.get("password") == "password":
        token = jwt.encode(
            {
                "user": data["username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # expires in 30 mins
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


# ---------------------------
# Protected Route (Requires JWT)
# ---------------------------
@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"message": "Token is missing!"}), 401

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({"message": f"Hello {decoded['user']}, you are authorized!"})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 401


if __name__ == "__main__":
    app.run(debug=True)
