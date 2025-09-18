from flask import Flask, request, jsonify
import json, datetime, uuid
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)

class StoreApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = "secret-key"  # Change to a secure key
        self.jwt = JWTManager(self.app)

        # Files
        self.USERS_FILE = "users.json"
        self.MASTER_FILE = "master.json"
        self.SLAVE_FILE = "slave.json"

        # Routes
        self.register_routes()

    # -------- Utility Methods --------
    def read_json(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return []

    def write_json(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    # -------- Routes --------
    def register_routes(self):
        @self.app.route("/register", methods=["POST"])
        def register():
            data = request.json
            users = self.read_json(self.USERS_FILE)

            # Only one master allowed
            if data["role"] == "master":
                if any(u["role"] == "master" for u in users):
                    return jsonify({"msg": "Master already exists!"}), 400

            data["id"] = str(uuid.uuid4())
            users.append(data)
            self.write_json(self.USERS_FILE, users)

            return jsonify({"msg": f"{data['role']} registered successfully", "id": data["id"]})

        @self.app.route("/login", methods=["POST"])
        def login():
            data = request.json
            users = self.read_json(self.USERS_FILE)

            user = next((u for u in users if u["name"] == data["name"] and u["password"] == data["password"]), None)
            if not user:
                return jsonify({"msg": "Invalid credentials"}), 401

            access_token = create_access_token(identity=user["id"])
            refresh_token = create_refresh_token(identity=user["id"])

            # log login
            entry = {
                "id": user["id"],
                "name": user["name"],
                "login": str(datetime.datetime.now()),
                "logout": None
            }

            if user["role"] == "master":
                logs = self.read_json(self.MASTER_FILE)
                logs.append(entry)
                self.write_json(self.MASTER_FILE, logs)
            else:
                logs = self.read_json(self.SLAVE_FILE)
                logs.append(entry)
                self.write_json(self.SLAVE_FILE, logs)

            return jsonify({"access_token": access_token, "refresh_token": refresh_token})

        @self.app.route("/logout", methods=["POST"])
        @jwt_required()
        def logout():
            user_id = get_jwt_identity()
            users = self.read_json(self.USERS_FILE)
            user = next((u for u in users if u["id"] == user_id), None)

            if not user:
                return jsonify({"msg": "User not found"}), 404

            file = self.MASTER_FILE if user["role"] == "master" else self.SLAVE_FILE
            logs = self.read_json(file)

            for log in reversed(logs):  # last entry
                if log["id"] == user["id"] and log["logout"] is None:
                    log["logout"] = str(datetime.datetime.now())
                    break

            self.write_json(file, logs)
            return jsonify({"msg": f"{user['role']} logged out successfully"})

        @self.app.route("/logs", methods=["GET"])
        @jwt_required()
        def view_logs():
            user_id = get_jwt_identity()
            users = self.read_json(self.USERS_FILE)
            user = next((u for u in users if u["id"] == user_id), None)

            if user["role"] != "master":
                return jsonify({"msg": "Access denied"}), 403

            master_logs = self.read_json(self.MASTER_FILE)
            slave_logs = self.read_json(self.SLAVE_FILE)
            return jsonify({"master_logs": master_logs, "slave_logs": slave_logs})

        @self.app.route("/refresh", methods=["POST"])
        @jwt_required(refresh=True)
        def refresh():
            user_id = get_jwt_identity()
            new_access_token = create_access_token(identity=user_id)
            return jsonify({"access_token": new_access_token})

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    app = StoreApp()
    app.run()
