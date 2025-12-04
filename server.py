# server.py
import json
from urllib.request import urlopen
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from flask import Flask, jsonify

class ClientCredsTokenValidator(JWTBearerTokenValidator):
    def __init__(self, issuer):
        jsonurl = urlopen(f"{issuer}/protocol/openid-connect/certs")
        public_key = JsonWebKey.import_key_set(
            json.loads(jsonurl.read())
        )
        super(ClientCredsTokenValidator, self).__init__(
            public_key
        )
        self.claims_options = {
            "exp": {"essential": True},
            "iss": {"essential": True, "value": issuer}
        }

require_auth = ResourceProtector() #decorator
validator = ClientCredsTokenValidator("http://localhost:8001/realms/myorg")
require_auth.register_token_validator(validator)

APP = Flask(__name__)

@APP.route("/api/public")
#@require_auth(None) #no scope req:auth header , only token is engough
def public():
    response = "No need of Authorization to see this"
    return jsonify(message=response)

@APP.route("/api/private")
@require_auth(None)
def private():
    response = "Authorization is required to see this"
    return jsonify(message=response)

@APP.route("/api/private-scoped")
@require_auth("test_api_access")#can give a list of scopes also
def private_scoped():
    response = "Authorization with a scope named test_api_access is required to see this"
    return jsonify(message=response)

APP.run(host="0.0.0.0", port=50100, debug=True)
