# server.py
from flask import Flask, jsonify


APP = Flask(__name__)

@APP.route("/api/public")
def public():
    response = "No need of Authorization to see this"
    return jsonify(message=response)

@APP.route("/api/private")
def private():
    response = "Authorization is required to see this"
    return jsonify(message=response)

@APP.route("/api/private-scoped")
def private_scoped():
    response = "Authorization with a scope named test_api_access is required to see this"
    return jsonify(message=response)

APP.run(host="0.0.0.0", port=50100, debug=True)