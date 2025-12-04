# OAuth2 Client‑Credentials Demo with Flask, Keycloak and Authlib

This project demonstrates how to secure a Flask API (resource server) using **Keycloak** as the **authorization server** and **Authlib** for JWT validation.

A separate Python script, `client.py`, acts as an **OAuth2 client** (machine‑to‑machine).  
It asks Keycloak for an access token and then calls the protected Flask API using that token.

---

## Architecture Overview

- **Keycloak (Authorization Server)**
  - Issues JWT access tokens.
  - Manages clients, scopes and keys.
  - Realm: `myorg`
  - Token endpoint:  
    `http://localhost:8001/realms/myorg/protocol/openid-connect/token`

- **Flask API – `server.py` (Resource Server)**
  - Exposes REST endpoints under `/api/...`
  - Validates incoming JWT access tokens using Authlib and Keycloak’s public keys.
  - Enforces scopes on specific endpoints (e.g. `test_api_access`).

- **Python Client – `client.py` (OAuth2 Client)**
  - Uses the **client credentials** grant to obtain a JWT from Keycloak.
  - Calls the protected Flask endpoint with `Authorization: Bearer <token>`.
  - Automates what you would otherwise do manually in Postman / REST client / jwt.io.

---


#### What `server.py` does
```a similar skeleton of the server is written in serverskeleton.py and a normal POSTMAN Access of tokens is given in client.http```
1. **Fetches Keycloak public keys**

   - In `ClientCredsTokenValidator.__init__`, the server calls:
     - `http://localhost:8001/realms/myorg/protocol/openid-connect/certs`
   - This is Keycloak’s **JWKS endpoint**.
   - The keys are used to verify the signature of incoming JWT access tokens.

2. **Validates standard JWT claims**

   - `exp` must be present and not expired.
   - `iss` must be exactly `http://localhost:8001/realms/myorg`.

3. **Registers `require_auth` decorator**

   - `require_auth = ResourceProtector()`
   - `require_auth.register_token_validator(validator)`
   - You can now use `@require_auth(...)` on each endpoint to control access.

4. **Defines three endpoints with different auth levels**

   - `/api/public`
     - No `@require_auth` → completely public, no token required.
   - `/api/private`
     - `@require_auth(None)`
     - Requires a **valid access token**, but **no specific scope**.
   - `/api/private-scoped`
     - `@require_auth("test_api_access")`
     - Requires:
       - A **valid access token** AND
       - The **scope** `test_api_access` to be present in the token’s `scope` claim.

> In other words:
> - If you *don’t* want an endpoint to require any scope → no decorator (public) or `@require_auth(None)` (auth only).
> - If you *do* want fine‑grained permission → use `@require_auth("some_scope")`.

---


#### What `client.py` does

`client.py` replaces the manual steps you would usually do in Postman, REST Client extension, or jwt.io:

1. **Obtain an access token from Keycloak**

   - Sends a POST request to the token endpoint:
     - `http://localhost:8001/realms/myorg/protocol/openid-connect/token`
   - Uses **client credentials grant**:
     - `grant_type=client_credentials`
     - `client_id=testapiclient1`
     - `client_secret=lient_secret>`
     - `scope=test_api_access` (explicitly asks Keycloak to include this scope)(if you choose OPTIONAL then must include this scope=...).

2. **Parses the JSON response**

   - Extracts `access_token` from Keycloak’s JSON response.
   - Prints the token (useful for debugging / inspecting in jwt.io).

3. **Calls the protected Flask endpoint**

   - Builds HTTP headers:

     ```
     apiReqHeaders = {
         "content-type": "application/json",
         "authorization": f"Bearer {accessToken}"
     }
     ```

   - Sends a GET request to the resource server:

     ```
     apiResp = requests.get(
         "http://localhost:50100/api/private-scoped",
         headers=apiReqHeaders
     )
     ```

   - If the token is:
     - Missing → the server returns `missing_authorization`.
     - Invalid / wrong issuer / expired → the server returns `invalid_token`.
     - Valid but lacks `test_api_access` → the server returns `403 insufficient_scope`.
     - Valid and contains `test_api_access` → you get HTTP 200 and the JSON message.

In short:

- **Keycloak** = Authentication / Authorization Server  
  - Issues JWTs, manages scopes and clients.
- **Flask `server.py`** = Resource Server  
  - Protects `/api/*` endpoints using JWT validation and scope checks.
- **`client.py`** = OAuth2 Client  
  - Automatically does:
    1. POST to Keycloak to get an access token (instead of using Postman/jwt.io).
    2. GET to the Flask API with `Authorization: Bearer <token>` header.

---


